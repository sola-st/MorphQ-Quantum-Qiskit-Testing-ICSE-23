from abc import ABC
from abc import abstractmethod

import os
import json
import random

from typing import Generator
from typing import Dict
from typing import Any
from typing import Tuple

import numpy as np
import math

from qasm_manipulation import remove_all_measurements
from qasm_manipulation import detect_registers
from qasm_manipulation import append_1Q_gate
from qasm_manipulation import get_first_and_only_quantum_register


class NoMoreProgramsAvailable(Exception):
    pass


class GenerationStrategy(ABC):

    def __init__(self, out_folder: str, benchmark_name: str):
        self.out_folder = out_folder
        self.benchmark_name = benchmark_name

    def generate(self,
                 n_qubits: int, n_ops_range: Tuple[int, int],
                 gate_set: Dict, random_seed: int, circuit_id: str) -> str:
        self.parse_metadata(n_qubits, n_ops_range, gate_set, random_seed)
        qasm_content, metadata = self._generate_single_program(circuit_id)
        self.store_qasm(circuit_id, qasm_content, self.out_folder, metadata)
        return qasm_content, metadata

    def parse_metadata(self,
                       n_qubits: int, n_ops_range: Tuple[int, int],
                       gate_set: Dict, random_seed: int):
        self.n_qubits = n_qubits
        self.min_n_ops = n_ops_range[0]
        self.max_n_ops = n_ops_range[1]
        self.gate_set = gate_set
        self.random_seed = random_seed

    @abstractmethod
    def _generate_single_program(self, circuit_id: str):
        """Generate QASM program and its metadata."""
        pass

    def store_qasm(self, filename: str, qasm_content: str,
                   out_folder: str, metadata_dict: Dict):
        """Save the results to a csv file."""
        metadata_dict["circuit_id"] = filename
        metadata_dict["benchmark_name"] = self.benchmark_name

        # save the metadata to a json file
        with open(os.path.join(out_folder, f"{filename}.json"), "w") as f:
            json.dump(metadata_dict, f)
            f.close()

        # save the qasm to a qasm file
        with open(os.path.join(out_folder, f"{filename}.qasm"), "w") as f:
            f.write(qasm_content)
            f.close()


class DerivationStrategy(GenerationStrategy):
    """Generate a program driving it from another existing program."""

    def load_existing_program(self, qasm_content: str, metadata: Dict[str, Any]) -> str:
        """Load an existing program."""
        self.ex_program_content = qasm_content
        self.ex_metadata = metadata


class WeightedRandomCircuitGenerator(GenerationStrategy):


    def random_circuit_encoding(self, n_ops, random_state):
        """Randomly generate an encoding for a circit."""
        return random_state.rand(3 * n_ops)

    def slot_to_gate(self, gates, gate_weights):
        """Map a slot to the gate name."""
        mapping_dict = dict()
        slot_to_assign = 0
        for gate, number_of_slots in zip(gates, gate_weights):
            for slot in range(number_of_slots):
                mapping_dict[slot_to_assign] = gate
                slot_to_assign += 1
        return mapping_dict

    def param_to_gate(self, param, gate_set):
        """Map a float parameter to a gate name."""
        map_slot_to_gate = self.slot_to_gate(gate_set.keys(), gate_set.values())
        slots = sum(gate_set.values())
        op_type = map_slot_to_gate[int(param / (float(1) / slots))]
        return op_type

    def generate_randomly(self, random_state, n_qubits: int, n_ops: int, gate_set: Dict[str, int]):
        """Random strategy: select a gate according to its weight.

        In practice we create an encoding ant then we map it to a specific sequence
        of gates.

        We have a list to encode the single operation, the final list looks like:
        (0.23, 0.75, 0.76, 0.44, etc)
        (gate_type, qubit, parameter, gate_type, qubit, parameter, etc...)
        The single operation is made of three floats:
        (gate_type, qubit, parameter)
        The first float encodes the gate. We divide the interval uniformly
        on the available gates:
        - CNOT
        - pauli X
        - pauli Y
        - pauli Z
        - pahse shift
        The second float encodes the qubit on which it applies to. We divide the
        interval uniformly on the available qubits.
        The third float is used only by:
        - cnot gate: to select a target qubit (similarly to the first flaot)
        - phase shift: to select the rotation
        Based on the second digit we decide on which qubit it acts on

        """
        circuit_qasm = 'OPENQASM 2.0;\ninclude "qelib1.inc";\n'
        encoding = self.random_circuit_encoding(
            n_ops=n_ops, random_state=random_state)
        qubits = range(n_qubits)
        # add quantum and classical registers
        circuit_qasm += f"qreg q[{n_qubits}];\n"
        circuit_qasm += f"creg c[{n_qubits}];\n"
        # get the single chunks
        n = 3  # number of parameters per operation
        chunks = [encoding[i:i + n] for i in range(0, len(encoding), n)]
        for op in chunks:
            # discard incomplete sequences
            if len(op) != 3:
                continue
            # get the type of gate
            op_type = self.param_to_gate(param=op[0], gate_set=gate_set)
            # print(op_type, " : ", op[0])
            try:
                # get target qubit
                qubit = qubits[int(op[1] / (float(1) / (len(qubits))))]
                # print(qubit, " : ", op[1])
                # extra parameter
                if op_type == "cx":
                    # get second target qubit
                    index_target = int(op[2] / (float(1) / (len(qubits) - 1)))
                    if index_target >= qubit:
                        index_target += 1
                    second_target_qubit = qubits[index_target]
                    # print(second_target_qubit, " : ", op[2])
                    # assert qubit == second_target_qubit, "Invalid encoding CNOT gate with same control and target qubit."
                    circuit_qasm += f"cx q[{qubit}], q[{second_target_qubit}];\n"
                elif op_type == "p":
                    # get rotation parameter
                    parameter = 2 * math.pi * op[2]
                    # print(parameter, " : ", op[2])
                    circuit_qasm += f"U(0,{parameter},0) q[{qubit}];\n"
                else:
                    parameter = 2 * math.pi * op[2]
                    # call the simple X, Y, Z gate on a single qubit
                    circuit_qasm += f"{op_type}({parameter}) q[{qubit}];\n"
            except IndexError:
                print(f"op[0]: {op[0]}")
                print(f"op[1]: {op[1]}")
                print(f"op[2]: {op[2]}")
                print(f"op_type: {op_type}")
                print(f"qubit: {qubit}")
                print(f"second_target_qubit: {second_target_qubit}")
        circuit_qasm += f"barrier q;\n"
        # Measure
        circuit_qasm += f"measure q -> c;\n"
        return circuit_qasm

    def _generate_single_program(self, circuit_id: str):
        """Generate a single QASM program."""
        print("-" * 80)
        print(f"Creating circuit: {circuit_id}")

        n_ops = random.randint(self.min_n_ops, self.max_n_ops)

        # generate a random circuit
        random_circuit_qasm_str = self.generate_randomly(
            n_qubits=self.n_qubits,
            n_ops=n_ops,
            gate_set=self.gate_set,
            random_state=np.random.RandomState(self.random_seed))

        metadata_dict = {
            "n_qubits": self.n_qubits,
            "n_ops": n_ops,
            "gate_set": self.gate_set,
            "strategy_program_generation": self.__class__.__name__
        }

        return random_circuit_qasm_str, metadata_dict


class FakeCircuitGenerator(GenerationStrategy):
    """Generate a fake circuit."""

    def _generate_single_program(self, circuit_id: str):
        """Generate QASM program and its metadata."""
        dumb_string = f"{self.n_qubits}  # number of qubits of the fake circuit"
        metadata_dict = {
            "n_qubits": self.n_qubits,
            "strategy_program_generation": self.__class__.__name__
        }
        return dumb_string, metadata_dict


class FamousCircuitGenerator(GenerationStrategy):
    """Generate a famous circuit."""

    def __init__(self, out_folder: str, benchmark_name: str):
        super().__init__(out_folder, benchmark_name)
        famous_algos_folder = "../data/QASMBench/famous_algos"
        # read all the file in the folder
        files = sorted(os.listdir(famous_algos_folder))
        file_contents_and_n_bits = []
        for file in files:
            with open(f"{famous_algos_folder}/{file}", "r") as f:
                content = f.read()
                f.close()
            n_bits = int(file.split("_")[1].replace("n", "").replace(".qasm", ""))
            file_contents_and_n_bits.append((content, n_bits))
        self.famous_algos = file_contents_and_n_bits
        self.available_algos = len(self.famous_algos)

    def _generate_single_program(self, circuit_id: str):
        """Generate QASM program and its metadata."""
        if self.available_algos > 0:
            self.available_algos -= 1
            algo, bits = self.famous_algos.pop()
            metadata_dict = {
                "n_qubits": bits,
                "strategy_program_generation": self.__class__.__name__
            }
            return algo, metadata_dict
        raise NoMoreProgramsAvailable("No more famous algos available.")


class FinalNotCircuitModifier(DerivationStrategy):

    def _generate_single_program(self, circuit_id: str):
        # remove the all measurement
        new_qasm, remove_measurement_section = remove_all_measurements(
            self.ex_program_content)
        # detect quantum registers
        first_qreg = get_first_and_only_quantum_register(new_qasm)
        n_qubits = first_qreg["n_qubits"]
        # append the final not gate
        new_qasm = append_1Q_gate(new_qasm, "x", list(range(n_qubits)))
        # update the n_ops count + number of not gates
        if "n_ops" in self.ex_metadata:
            self.ex_metadata["n_ops"] += n_qubits
        # append the measurement (removed previously)
        new_qasm += "\n" + remove_measurement_section
        return new_qasm, self.ex_metadata



