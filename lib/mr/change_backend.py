import ast
from copy import deepcopy
from functools import reduce
import numpy as np
import re
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class ChangeBackend(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        return metamorph.check_get_backend(code_of_source)

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Change the backend used in the source code.

        Args:
            source_code: The source code of the circuit.
            available_backends: available backends to use.

        Returns:
            The source code of the circuit with the backend changed.
        """
        available_backends = self.mr_config["available_backends"]
        sections = metamorph.get_sections(code_of_source)
        execution_section = sections["EXECUTION"]
        mr_metadata = {}

        tree = ast.parse(execution_section)

        class BackendChanger(ast.NodeTransformer):

            def __init__(self, available_backends: List[str]):
                self.available_backends = deepcopy(available_backends)

            def visit_Call(self, node):
                if (isinstance(node, ast.Call) and
                        isinstance(node.func, ast.Attribute) and
                        node.func.attr == "get_backend" and
                        isinstance(node.args[0], ast.Constant)):
                    if node.args[0].value in self.available_backends:
                        self.available_backends.remove(node.args[0].value)
                    target_backend = np.random.choice(self.available_backends)
                    print(f"Follow: replace backend {node.args[0].value} -> " +
                          f"{target_backend}")
                    mr_metadata["initial_backend"] = str(node.args[0].value)
                    mr_metadata["new_backend"] = str(target_backend)
                    node.args[0].value = target_backend
                return node

        backend_changer = BackendChanger(available_backends)
        modified_tree = backend_changer.visit(tree)
        changed_section = metamorph.to_code(modified_tree)
        sections["EXECUTION"] = changed_section

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)

    def check_output_relationship(
            self,
            result_a: Dict[str, int],
            result_b: Dict[str, int]) -> bool:
        """Check that the two results are equivalent."""
        exec_metadata = {
            "res_A": result_a,
            "res_B": result_b
        }
        detectors = self.detectors
        return detect_divergence(exec_metadata, detectors)
