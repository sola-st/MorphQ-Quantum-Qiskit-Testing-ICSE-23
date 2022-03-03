import ast
from copy import deepcopy
from functools import reduce
import numpy as np
import re
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class ChangeTargetBasis(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        return metamorph.check_transpile(code_of_source)

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Change the basic gates used in the source code (via transpile).
        """
        universal_gate_sets = self.mr_config["universal_gate_sets"]
        target_gates = np.random.choice(universal_gate_sets)["gates"]
        sections = metamorph.get_sections(code_of_source)
        opt_level_section = sections["OPTIMIZATION_LEVEL"]
        mr_metadata = {}

        tree = ast.parse(opt_level_section)

        class BasisChanger(ast.NodeTransformer):

            def __init__(self, target_gates: List[str]):
                self.target_gates = target_gates

            def visit_Call(self, node):
                if (isinstance(node, ast.Call) and
                        isinstance(node.func, ast.Name) and
                        node.func.id == "transpile"):
                    args = [k.arg for k in node.keywords]
                    if "basis_gates" in args:
                        idx = args.index("basis_gates")
                        node.keywords[idx].value = ast.List(elts=[
                            ast.Constant(g_name) for g_name in self.target_gates
                        ])
                        mr_metadata["new_basis_gates"] = self.target_gates
                        print("Follow: gateset replaced with: ", self.target_gates)
                return node

        changer = BasisChanger(target_gates)
        modified_tree = changer.visit(tree)
        changed_section = metamorph.to_code(modified_tree)
        sections["OPTIMIZATION_LEVEL"] = changed_section

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
