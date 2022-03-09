import ast
from functools import reduce
import numpy as np
import re
import random
from typing import List, Tuple, Dict, Any

from lib.mr import MetamorphicTransformation

import lib.metamorph as metamorph
from lib.qfl import detect_divergence


class RunIndependentPartitions(MetamorphicTransformation):

    def check_precondition(self, code_of_source: str) -> bool:
        # NB: this checks that there is also only one circuit (implicitly)
        return metamorph.check_separable(
            code_of_source,
            n_partitions=self.mr_config["n_partitions"])

    def is_semantically_equivalent(self) -> bool:
        return False

    def derive(self, code_of_source: str) -> str:
        """Run the n_partitions separately and aggregate.
        """
        n_partitions = self.mr_config["n_partitions"]

        sections = metamorph.get_sections(code_of_source)
        mr_metadata = {}
        # print(code_of_source)
        circuits = metamorph.get_circuits_used(circ_definition=sections["CIRCUIT"])

        # after the precondition we are guardanteed that there is only
        # one circuit
        main_circuit = circuits[0]
        # print(main_circuit)

        circuit = sections["CIRCUIT"]
        instruction_lines = [
            line for line in circuit.split("\n")
            if ".append(" in line]

        lines_and_qubits = []
        register_name = main_circuit['quantum_register']

        all_used_qubits = []
        for line in instruction_lines:
            qubits_involved = [
                int(q) for q in re.findall(fr"{register_name}\[(\d+)\]", line)]
            lines_and_qubits.append([line, qubits_involved])
            all_used_qubits += qubits_involved
        all_used_qubits = set(all_used_qubits)
        all_available_qubits = set(list(range(main_circuit['size'])))
        unused_qubits = all_available_qubits.difference(all_used_qubits)

        connected_qubit_clusters = metamorph.cluster_qubits(
            circuit_code=circuit,
            circuit_name=main_circuit['name'],
            register_name=main_circuit['quantum_register'])

        print(connected_qubit_clusters)

        safe_counter = 0
        partition_indices = []
        while len(list(set(partition_indices))) < n_partitions:
            partition_indices = np.random.choice(
                np.arange(n_partitions), size=len(connected_qubit_clusters))
            safe_counter += 1
            if safe_counter > 100:
                raise Exception("Could not find a valid partitioning")

        print(partition_indices)

        new_subcircuits = []

        self.full_mapping = {}

        code_partitions = []

        shift = 0

        for i_partition in range(n_partitions):
            clusters_of_this_partition = [
                cluster
                for owner, cluster in zip(
                    partition_indices, connected_qubit_clusters)
                if owner == i_partition]
            print("clusters_of_this_partition", clusters_of_this_partition)
            qubits_of_this_partition = [
                list(cluster) for cluster in clusters_of_this_partition]
            qubits_of_this_partition = [
                item
                for sublist in qubits_of_this_partition
                for item in sublist]
            if i_partition == 0:
                # some circuits might use less qubits, then those available,
                # thus the remaining unused qubits are added to the first
                # partition by default
                qubits_of_this_partition += unused_qubits
            print(f"{i_partition} partition) qubits_of_this_partition: " +
                  f"{qubits_of_this_partition}")
            mr_metadata[f"partition_{i_partition}"] = \
                qubits_of_this_partition
            partition_mapping = {}
            for qubit_subcircuit_idx, qubit_original_idx in enumerate(
                    qubits_of_this_partition):
                partition_mapping[qubit_original_idx] = \
                    qubit_subcircuit_idx
                self.full_mapping[qubit_original_idx] = \
                    shift + qubit_subcircuit_idx
            mr_metadata[f"partition_{i_partition}_mapping"] = \
                partition_mapping

            code_new_subcircuit_header = metamorph.create_empty_circuit(
                id_quantum_reg=f"qr_{i_partition+1}",
                id_classical_reg=f"cr_{i_partition+1}",
                id_circuit=f"qc_{i_partition+1}",
                n_qubits=len(qubits_of_this_partition))

            new_subcircuit_info = {
                'name': f"qc_{i_partition+1}",
                'quantum_register': f"qr_{i_partition+1}",
                'classical_register': f"cr_{i_partition+1}",
                'size': len(qubits_of_this_partition)}
            new_subcircuits.append(new_subcircuit_info)
            shift += len(qubits_of_this_partition)

            instructions_in_this_partition = []
            for line, qubits_involved in lines_and_qubits:
                if set(qubits_involved).issubset(qubits_of_this_partition):
                    instructions_in_this_partition.append(line)

            code_instructions = "\n".join(instructions_in_this_partition)

            for entity in ['name', 'quantum_register', 'classical_register']:
                code_instructions = metamorph.replace_identifier(
                    source_code=code_instructions,
                    identifier=main_circuit[entity],
                    replacement=new_subcircuit_info[entity])

            code_instructions = metamorph.remap_qubits(
                source_code=code_instructions,
                id_quantum_reg=new_subcircuit_info['quantum_register'],
                id_classical_reg=new_subcircuit_info['classical_register'],
                mapping=partition_mapping)

            code_partition = \
                code_new_subcircuit_header + "\n" + code_instructions
            code_partitions.append(code_partition)

        mr_metadata['subcircuits'] = new_subcircuits
        new_circuit_code = "\n".join(code_partitions)
        sections["CIRCUIT"] = new_circuit_code

        # create mapping from old qubit indices to pairs:
        # (subcircuit_name, new_qubit_index)

        # remap the instruction using the mapping
        # for all instructions change the circuit and qubits they are acting on

        if "PARAMETER_BINDING" in sections.keys():
            sections["PARAMETER_BINDING"] = self._circuit_specific_bindings(
                new_circuit_code=new_circuit_code,
                old_binding_code=sections["PARAMETER_BINDING"]
            )


        if "USELESS_ENTITIES" in sections.keys():
            sections["USELESS_ENTITIES"] = sections["USELESS_ENTITIES"].replace(
                f"{main_circuit['name']}.add_register",
                f"{random.choice(new_subcircuits)['name']}.add_register"
            )

        sections_to_duplicate = [
            "OPTIMIZATION_LEVEL", "MEASUREMENT", "EXECUTION"]
        if "QASM_CONVERSION" in sections.keys():
            sections_to_duplicate.append("QASM_CONVERSION")
        for sections_name in sections_to_duplicate:
            c_section = sections[sections_name]
            new_lines = [
                line if main_circuit["name"] not in line else "\n".join([
                    line.replace(
                        main_circuit["name"], f"qc_{i+1}").replace(
                        main_circuit["quantum_register"], f"qr_{i+1}").replace(
                        main_circuit["classical_register"], f"cr_{i+1}").replace(
                        "counts =", f"counts_{i+1} =")
                    for i in range(n_partitions)
                ])
                for line in c_section.split("\n")
            ]
            new_section = "\n".join(new_lines)
            sections[sections_name] = new_section

        counter_identifiers = [
            "counts_" + str(i+1) for i in range(n_partitions)]
        counter_identifiers_str = ", ".join(counter_identifiers)

        sections["EXECUTION"] = sections["EXECUTION"].replace(
            "RESULT = counts",
            f"RESULT = [{counter_identifiers_str}]")

        mr_metadata["mapping"] = self.full_mapping
        self.metadata = mr_metadata

        return metamorph.reconstruct_sections(sections)

    def check_output_relationship(
            self,
            result_a: Dict[str, int],
            result_b: Dict[str, int]) -> bool:
        """Check that the two results are equivalent.

        Note that we read the followup output according to the qubit mapping.
        """
        result_b = self._reconstruct(result_b)
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

    def _reconstruct(self, counts: List[Dict[str, int]]):
        """Pass the count results.

        NB: list the circuit working on lower qubit indices first.
        """
        result_concatenated = reduce(lambda counts_1, counts_2: {
            k2 + k1: v1 * v2 for k1, v1 in counts_1.items()
            for k2, v2 in counts_2.items()
        }, counts)
        result_b = {
            self._read_str_with_mapping(bitstring, self.full_mapping): freq
            for bitstring, freq in result_concatenated.items()
        }
        return result_b

    def _circuit_specific_bindings(
            self, new_circuit_code: str, old_binding_code: str):
        """Create n bind_parameters calls with the respective params.

        Note that each subcircuit will have bindings only for the parameters
        used in its definition.
        """
        instructions = metamorph.get_instructions(new_circuit_code)
        current_binding_str = re.search(
            r"bind_parameters\(\{([a-zA0-9_ ,:\.]+)\}", old_binding_code).group(1)
        current_binding_dict = {
            chunk.split(":")[0].strip(): float(chunk.split(":")[1])
            for chunk in current_binding_str.split(",")
        }

        available_circuits = list(set(
            [e['circuit_id'] for e in instructions]
        ))
        new_binding_code = ""
        for circuit_id in available_circuits:
            c_circuit_parameters = []
            for instr in instructions:
                if instr['circuit_id'] == circuit_id:
                    str_parameters = \
                        [p for p in instr["params"] if isinstance(p, str)]
                    c_circuit_parameters += str_parameters
            c_circuit_binding_dict = {
                k: v
                for k, v in current_binding_dict.items()
                if k in c_circuit_parameters
            }
            new_binding_code += \
                f"{circuit_id} = {circuit_id}.bind_parameters(" + \
                f"{c_circuit_binding_dict})\n"

        return new_binding_code
