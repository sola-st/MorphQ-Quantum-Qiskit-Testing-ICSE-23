import ast
import numpy as np
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class ChangeQubitOrder(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        return True

    def is_semantically_equivalent(self) -> bool:
        return False

    def derive(self, code_of_source: str) -> str:
        """Scramble the order of qubits."""
        scramble_percentage = self.mr_config['scramble_percentage']
        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]
        tree = ast.parse(source_code_circuit)
        mr_metadata = {}

        registers = metamorph.get_registers_used(source_code_circuit)
        # we assume to have exactly one quantum and one classical register
        # and they have the same number of qubits
        quantum_reg = [r for r in registers
                       if r["type"] == "QuantumRegister"][0]
        classical_reg = [r for r in registers
                         if r["type"] == "ClassicalRegister"][0]
        assert(quantum_reg["size"] == classical_reg["size"])

        n_idx = quantum_reg["size"]
        idx_to_scramble = np.random.choice(
            list(range(n_idx)),
            size=int(n_idx * scramble_percentage), replace=False)
        mapping = metamorph.create_random_mapping(idx_to_scramble)
        mr_metadata["mapping"] = str(mapping)

        class QubitOrderChanger(ast.NodeTransformer):

            def __init__(self,
                         id_quantum_reg: str,
                         id_classical_reg: str, mapping: Dict[int, int]):
                self.id_quantum_reg = id_quantum_reg
                self.id_classical_reg = id_classical_reg
                self.mapping = mapping

            def visit_Subscript(self, node):
                if (isinstance(node, ast.Subscript) and
                        isinstance(node.value, ast.Name) and
                        (node.value.id == self.id_quantum_reg or
                        node.value.id == self.id_classical_reg) and
                        isinstance(node.slice, ast.Index) and
                        isinstance(node.slice.value, ast.Constant) and
                        node.slice.value.value in self.mapping.keys()):
                    node.slice.value.value = self.mapping[node.slice.value.value]
                return node

        changer = QubitOrderChanger(
            id_quantum_reg=quantum_reg["name"],
            id_classical_reg=classical_reg["name"],
            mapping=mapping)
        modified_tree = changer.visit(tree)
        print("Follow: indices mapping: ", mapping)
        changed_section = metamorph.to_code(modified_tree)
        sections["CIRCUIT"] = changed_section

        self.full_mapping = {**mapping, **{
            i: i for i in range(n_idx) if i not in mapping.keys()}}

        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)

    def check_output_relationship(
            self,
            result_a: Dict[str, int],
            result_b: Dict[str, int]) -> bool:
        """Check that the two results are equivalent.

        Note that we read the followup output according to the qubit mapping.
        """
        result_b = {
            self._read_str_with_mapping(bitstring, self.full_mapping): freq
            for bitstring, freq in result_b.items()
        }
        exec_metadata = {
            "res_A": result_a,
            "res_B": result_b
        }
        detectors = self.detectors
        return detect_divergence(exec_metadata, detectors)

    def _read_str_with_mapping(
            self,
            bitstring: str,
            direct_mapping: Dict[int, int]) -> str:
        """Given a bitstring convert it to the original mapping."""
        n_bits = len(bitstring)
        bitstring = bitstring[::-1]
        return "".join([bitstring[direct_mapping[i]]
                        for i in range(n_bits)])[::-1]
