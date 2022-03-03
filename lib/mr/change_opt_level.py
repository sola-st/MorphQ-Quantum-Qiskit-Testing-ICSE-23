import ast
import numpy as np
from copy import deepcopy
import numpy as np

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph

from typing import List, Tuple, Dict, Any


class ChangeOptLevel(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        return metamorph.check_function_call_in_code(
            code_of_source, "transpile")

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Change the optimization level (via transpile).
        """

        sections = metamorph.get_sections(code_of_source)
        opt_level_section = sections["OPTIMIZATION_LEVEL"]
        mr_metadata = {}

        tree = ast.parse(opt_level_section)

        class OptLevelChanger(ast.NodeTransformer):

            def __init__(self, levels: List[int]):
                self.levels = deepcopy(levels)

            def visit_Call(self, node):
                if (isinstance(node, ast.Call) and
                        isinstance(node.func, ast.Name) and
                        node.func.id == "transpile"):
                    args = [k.arg for k in node.keywords]
                    if "optimization_level" in args:
                        initial_level = node.keywords[
                            args.index("optimization_level")].value.value
                        self.levels.remove(initial_level)
                        target_opt_level = int(np.random.choice(self.levels))
                        node.keywords[args.index("optimization_level")].value = \
                            ast.Constant(target_opt_level)
                        mr_metadata["initial_level"] = int(initial_level)
                        mr_metadata["new_level"] = int(target_opt_level)
                        print(f"Follow: optimization level changed:" +
                              f" {initial_level} -> {target_opt_level}")
                return node

        changer = OptLevelChanger(levels=self.mr_config["levels"])
        modified_tree = changer.visit(tree)
        changed_section = metamorph.to_code(modified_tree)
        sections["OPTIMIZATION_LEVEL"] = changed_section

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
