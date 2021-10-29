import numpy as np
import cirq
import qiskit
from qiskit.circuit import qpy_serialization
from qiskit import QuantumCircuit
from typing import List
import math
import pandas as pd
from IPython.display import display
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

import json
import random
import os
import hashlib

from functools import partial
from multiprocessing import Pool

from simulators import *


N_QUBITS = 10
N_OPS = 100
N_EVALUATIONS = 100
TOP_K_SOLUTION_TO_COMPARE = 5
CLASSICAL_INPUT = 127
SEED_NP = 42
OUT_FOLDER = "../data/random_program_execution"

QASM_HEADER = """
OPENQASM 2.0;
include "qelib1.inc";
"""

gate_set = {
    "cx": 3,
    "rx": 1,
    "ry": 1,
    "rz": 1,
    "p": 1
}

# Utility functions


def random_circuit_encoding(n_ops=N_OPS, random_state=None):
    """Randomly generate an encoding for a circit."""
    if random_state is not None:
        assert isinstance(random_state, int)
        np.random.seed(random_state)
    return np.random.rand(3 * n_ops)


def slot_to_gate(gates, gate_weights):
    """Map a slot to the gate name."""
    mapping_dict = dict()
    slot_to_assign = 0
    for gate, number_of_slots in zip(gates, gate_weights):
        for slot in range(number_of_slots):
            mapping_dict[slot_to_assign] = gate
            slot_to_assign += 1
    return mapping_dict


def param_to_gate(param, gate_set):
    """Map a float parameter to a gate name."""
    map_slot_to_gate = slot_to_gate(gate_set.keys(), gate_set.values())
    slots = sum(gate_set.values())
    op_type = map_slot_to_gate[int(param / (float(1) / slots))]
    return op_type


def encoding_to_circuit(encoding: List[float], n_qubits: int, classical_input: int = None):
    """Convert encoding to a qasm string.

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
    circuit_qasm = QASM_HEADER
    qubits = range(n_qubits)

    # add quantum and classical registers
    circuit_qasm += f"qreg q[{n_qubits}];\n"
    circuit_qasm += f"creg c[{n_qubits}];\n"


    if classical_input != None:
        assert isinstance(classical_input, int)
        format_string = "{0:" + str(n_qubits) + "b}"
        string_input = format_string.format(classical_input).zfill(n_qubits)
        for i, c in enumerate(string_input):
            if c == "1":
                circuit_qasm += f"x q[{i}];\n"

    circuit_qasm += f"barrier q;\n"


    # get the single chunks
    n = 3  # number of parameters per operation
    chunks = [encoding[i:i + n] for i in range(0, len(encoding), n)]
    for op in chunks:
        # discard incomplete sequences
        if len(op) != 3:
            continue
        # get the type of gate
        op_type = param_to_gate(param=op[0], gate_set=gate_set)
        #print(op_type, " : ", op[0])

        try:
            # get target qubit
            qubit = qubits[int(op[1] / (float(1) / (len(qubits))))]
            #print(qubit, " : ", op[1])

            # extra parameter
            if op_type == "cx":
                # get second target qubit
                index_target = int(op[2] / (float(1) / (len(qubits) - 1)))
                if index_target >= qubit:
                    index_target += 1
                second_target_qubit = qubits[index_target]
                #print(second_target_qubit, " : ", op[2])
                #assert qubit == second_target_qubit, "Invalid encoding CNOT gate with same control and target qubit."
                circuit_qasm += f"cx q[{qubit}], q[{second_target_qubit}];\n"
            elif op_type == "p":
                # get rotation parameter
                parameter = 2 * math.pi * op[2]
                #print(parameter, " : ", op[2])
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


def generate_circuit():
    """Generate a new circuit with evaluations."""
    print("-" * 80)
    print(f"Creating circuit number")

    classical_input = random.randint(0, 2 ** N_QUBITS - 1)

    # create a new random circuit
    numerical_encoding = random_circuit_encoding(n_ops=N_OPS)
    random_circuit_qasm_str = encoding_to_circuit(
        encoding=numerical_encoding,
        n_qubits=N_QUBITS,
        classical_input=classical_input)

    # evaluate circuits
    platforms = [QiskitCircuit(), CirqCircuit()]
    platform_result_dfs = []

    print(f"Running (via simulation)")
    # for each platform in (qiskit, cirq, etc)
    for p in platforms:
        print(p.platform_name)

        # create a circuit object form the qasm file
        p.from_qasm(random_circuit_qasm_str)

        # perform 30 evaluations [N_EVALUATION]
        data = []
        for i in range(N_EVALUATIONS):
            # run the circuit for 1024 or 8096 shots
            p.execute()
            data.append(p.get_result())

        # save the statistics for each combination to a dataframe
        df = pd.DataFrame.from_records(data)
        platform_result_dfs.append(df)

    for df in platform_result_dfs:
        display(df.head())

    df_qiskit, df_cirq = platform_result_dfs
    metadata_dict = {
        "encoding": list(numerical_encoding),
        "classical_input": classical_input,
        "n_qubits": N_QUBITS,
        "n_evaluations": N_EVALUATIONS,
        "n_ops": N_OPS,
        "gate_set_weights": gate_set
    }

    print(f"Saving circuit: with simulation results")
    save(out_folder=OUT_FOLDER, metadata_dict=metadata_dict,
         df_platform_a=df_qiskit, df_platform_b=df_cirq,
         platform_a_name="qiskit", platform_b_name="cirq")


def save(out_folder: str, metadata_dict: dict,
         df_platform_a: pd.DataFrame, df_platform_b: pd.DataFrame,
         platform_a_name: str, platform_b_name: str):
    """Save the results to a csv file."""
    # save the metadata to a json file
    assert "encoding" in metadata_dict.keys()
    numerical_encoding = str(metadata_dict["encoding"])
    hash_encoding = hashlib.sha256(numerical_encoding.encode()).hexdigest()
    with open(os.path.join(out_folder, f"{hash_encoding}.json"), "w") as f:
        json.dump(metadata_dict, f)
    df_platform_a.to_csv(
        os.path.join(out_folder, f"{hash_encoding}_{platform_a_name}.csv"))
    df_platform_b.to_csv(
        os.path.join(out_folder, f"{hash_encoding}_{platform_b_name}.csv"))


def main():
    """Simulate circuits."""
    for i in range(1000):
        generate_circuit()


if __name__ == "__main__":
    main()