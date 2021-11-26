
import click
import yaml

import numpy as np
import math

import json
import random
import os
import time

from simulators import *

from typing import Dict, Any

QASM_HEADER = """
OPENQASM 2.0;
include "qelib1.inc";
"""

# Utility functions


def random_circuit_encoding(n_ops, random_state):
    """Randomly generate an encoding for a circit."""
    return random_state.rand(3 * n_ops)


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


def generate_randomly(random_state, n_qubits: int, n_ops: int, gate_set: Dict[str, int]):
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
    circuit_qasm = QASM_HEADER
    encoding = random_circuit_encoding(
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


def generate_circuit(config: Dict[str, Any]):
    """Generate a new circuit with evaluations."""
    print("-" * 80)
    print(f"Creating circuit number")

    n_qubits = random.randint(config["min_n_qubits"], config["max_n_qubits"])
    n_ops = random.randint(config["min_n_ops"], config["max_n_ops"])

    if (config["strategy_program_generation"] == "uniform" or
            config["strategy_program_generation"] == "weighted"):
        gate_set = config["gate_set"]
        if (config["strategy_program_generation"] == "uniform"):
            for gate in gate_set.keys():
                gate_set[gate] = 1
        # generate a random circuit
        random_circuit_qasm_str = generate_randomly(
            n_qubits=n_qubits,
            n_ops=n_ops,
            gate_set=gate_set,
            random_state=np.random.RandomState(config["random_seed"]))


    metadata_dict = {
        "n_qubits": n_qubits,
        "n_ops": n_ops,
        "gate_set": config["gate_set"],
        "strategy_program_generation": config["strategy_program_generation"]
    }

    print(f"Saving circuit: with simulation results")
    timestamp = int(time.time())
    qasm_file_name = config["program_id_pattern"]
    qasm_file_name = \
        qasm_file_name.replace("{{timestamp}}", str(timestamp))
    qasm_file_name = \
        qasm_file_name.replace("{{randint}}", str(random.randint(0, 9999)).zfill(4))
    print(f"qasm_file_name: {qasm_file_name}")
    # get current timestamp as integer and use it as filename

    store_qasm(
        filename=qasm_file_name,
        qasm_content=random_circuit_qasm_str,
        out_folder=config["folder_generated_qasm"],
        metadata_dict=metadata_dict
    )


def store_qasm(filename: str, qasm_content: str, out_folder: str, metadata_dict: dict):
    """Save the results to a csv file."""
    # save the metadata to a json file
    with open(os.path.join(out_folder, f"{filename}.json"), "w") as f:
        json.dump(metadata_dict, f)
        f.close()

    # save the qasm to a qasm file
    with open(os.path.join(out_folder, f"{filename}.qasm"), "w") as f:
        f.write(qasm_content)
        f.close()



@click.command()
@click.argument('config_file')
def main(config_file):
    """Generate programs according to the CONFIG_FILE."""
    # check that there is a file at the config file location
    assert os.path.isfile(config_file), "Config file does not exist."
    # load the config file with yaml
    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    # check that the config file has the right keys
    keys = config.keys()
    required_keys = [
        "min_n_qubits", "max_n_qubits",
        "min_n_ops", "max_n_ops",
        "program_id_pattern",
        "random_seed", "n_generated_programs",
        "gate_set", "strategy_program_generation",
        "folder_generated_qasm"]
    for req_key in required_keys:
        assert req_key in keys, f"Config file missing key: {req_key}"

    for _ in range(config["n_generated_programs"]):
        generate_circuit(config)


if __name__ == '__main__':
    main()