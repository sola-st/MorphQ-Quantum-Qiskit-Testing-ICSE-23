import ast
from copy import deepcopy
from functools import reduce
import numpy as np
import re
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence
from lib.generation_strategy_python import *
from lib.generation_strategy_python import Fuzzer


class InjectNullEffect(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        return metamorph.check_single_circuit(code_of_source)

    def is_semantically_equivalent(self) -> bool:
        return True

    def derive(self, code_of_source: str) -> str:
        """Inject a subcircuit and its inverse with a null effect overall."""
        min_n_ops = self.mr_config["min_n_ops"]
        max_n_ops = self.mr_config["max_n_ops"]
        fuzzer_object = self.mr_config["fuzzer_object"]
        gate_set = self.mr_config["gate_set"]

        sections = metamorph.get_sections(code_of_source)
        source_code_circuit = sections["CIRCUIT"]
        mr_metadata = {}
        registers = metamorph.get_registers_used(source_code_circuit)
        # we assume to have exactly one quantum and one classical register
        # and they have the same number of qubits
        quantum_reg = [r for r in registers
                       if r["type"] == "QuantumRegister"][0]
        classical_reg = [r for r in registers
                         if r["type"] == "ClassicalRegister"][0]
        assert(quantum_reg["size"] == classical_reg["size"])
        n_bits_declared = quantum_reg["size"]

        n_ops = np.random.randint(min_n_ops, max_n_ops)
        mr_metadata["n_ops"] = n_ops
        mr_metadata["fuzzer_object"] = fuzzer_object

        id_sub_circuit, subcirc_source_code = metamorph.create_circuit(
            id_quantum_reg=quantum_reg['name'],
            id_classical_reg=classical_reg['name'],
            id_circuit="subcircuit",
            n_qubits=n_bits_declared,
            n_ops=n_ops,
            gate_set=gate_set,
            generator_name=fuzzer_object,
            only_circuit=True)

        main_circuit_id = metamorph.get_circuit_via_regex(source_code_circuit)

        if main_circuit_id is None:
            raise Exception("Could not find main circuit id.")

        all_lines = source_code_circuit.split("\n")
        lines_to_inject = subcirc_source_code.split("\n")
        # the generated circuit might contain the header of a new circuit section
        # remove it by removing all comment lines
        lines_to_inject = [line for line in lines_to_inject
                           if not line.startswith("#")]
        lines_to_inject.append(
            f"{main_circuit_id}.append({id_sub_circuit}, qargs={quantum_reg['name']}, cargs={classical_reg['name']})")
        lines_to_inject.append(
            f"{main_circuit_id}.append({id_sub_circuit}.inverse(), qargs={quantum_reg['name']}, cargs={classical_reg['name']})")

        mask_suitable_lines = [
            line.startswith(f"{main_circuit_id}.append(")
            for line in all_lines]
        possible_insertion_points = np.where(np.array(mask_suitable_lines))[0]
        if len(possible_insertion_points) > 0:
            # sometime the main generated circuit is empty
            insertion_point = np.random.choice(possible_insertion_points)
        else:
            insertion_point = len(all_lines) - 1

        for injected_line in lines_to_inject[::-1]:
            all_lines.insert(insertion_point, injected_line)

        changed_section = "\n".join(all_lines)
        sections["CIRCUIT"] = changed_section

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
