import ast
import random
import numpy as np
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class QdiffG1SwapToCnot(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        """Check if there is a swap gate in the following circuit."""
        class SwapCounter(ast.NodeVisitor):

            def __init__(self):
                self.swap_counter = 0

            def recursive(func):
                """ decorator to make visitor work recursive """
                def wrapper(self, node):
                    func(self, node)
                    for child in ast.iter_child_nodes(node):
                        self.visit(child)
                return wrapper

            @recursive
            def visit_Call(self, node):
                if (isinstance(node, ast.Call) and
                        isinstance(node.func, ast.Attribute) and
                        (node.func.attr == "append") and
                        isinstance(node.args[0], ast.Call) and
                        isinstance(node.args[0].func, ast.Name) and
                        (node.args[0].func.id == "SwapGate")):
                    self.swap_counter += 1

        tree = ast.parse(code_of_source)
        counter = SwapCounter()
        counter.generic_visit(tree)
        self.tot_n_swap_gates = counter.swap_counter

        return self.tot_n_swap_gates > 0

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Replace a swap gate with two CNOT gates."""
        min_to_change = self.mr_config['min_to_change']
        max_to_change = self.mr_config['max_to_change']
        n_gate_to_change = random.randint(min_to_change, max_to_change)
        max_to_change = min(n_gate_to_change, self.tot_n_swap_gates)
        to_be_changed_vector = np.zeros(self.tot_n_swap_gates)
        to_be_changed_vector[:n_gate_to_change] = 1
        # randomize the vector
        self.to_be_changed_vector = np.random.permutation(to_be_changed_vector)

        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]
        tree = ast.parse(source_code_circuit)

        mr_metadata = {}
        mr_metadata["replacement_swap"] = str(self.to_be_changed_vector)

        class ReplaceSwaps(ast.NodeTransformer):

            def __init__(self, to_be_changed_vector):
                self.to_be_changed_vector = to_be_changed_vector
                self.current_swap_position = 0

            def is_swap_node(self, node: ast.AST) -> bool:
                """Check if the node is a swap gate."""
                return (isinstance(node, ast.Expr) and
                        isinstance(node.value, ast.Call) and
                        isinstance(node.value.func, ast.Attribute) and
                        (node.value.func.attr == "append") and
                        isinstance(node.value.args[0], ast.Call) and
                        isinstance(node.value.args[0].func, ast.Name) and
                        (node.value.args[0].func.id == "SwapGate"))

            def substitute_swap(self, swap_node: ast.AST) -> List[ast.AST]:
                """Substitute the swap gates with CNOT gates."""
                circuit_name = swap_node.value.func.value.id
                bits = swap_node.value.keywords[0].value.elts
                reverse_bits = bits[::-1]

                direct_cnot = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=circuit_name),
                            attr="append",
                        ),
                        args=[
                            ast.Call(
                                func=ast.Name(
                                    id="CXGate"
                                ),
                                args=[],
                                keywords=[],
                            )
                        ],
                        keywords=[
                            ast.keyword(
                                arg="qargs",
                                value=ast.List(elts=bits)
                            ),
                            ast.keyword(
                                arg="cargs",
                                value=ast.List(elts=[])
                            )
                        ],
                    )
                )
                reversed_cnot = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=circuit_name),
                            attr="append",
                        ),
                        args=[
                            ast.Call(
                                func=ast.Name(
                                    id="CXGate"
                                ),
                                args=[],
                                keywords=[],
                            )
                        ],
                        keywords=[
                            ast.keyword(
                                arg="qargs",
                                value=ast.List(elts=reverse_bits)
                            ),
                            ast.keyword(
                                arg="cargs",
                                value=ast.List(elts=[])
                            )
                        ],
                    )
                )
                return [direct_cnot, reversed_cnot, direct_cnot]

            def visit_Expr(self, node):
                if self.is_swap_node(node):
                    if self.to_be_changed_vector[
                            self.current_swap_position] == 1:
                        new_node = self.substitute_swap(node)
                    else:
                        new_node = [node]
                    self.current_swap_position += 1
                    return new_node
                return node

        changer = ReplaceSwaps(self.to_be_changed_vector)
        tree = ast.parse(source_code_circuit)
        modified_tree = changer.visit(tree)
        changed_section = metamorph.to_code(modified_tree)
        sections["CIRCUIT"] = changed_section

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)
