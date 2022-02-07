
"""Interface to run quantum circuits on different platforms.

It supports conversion from qasm to the platform-specific circuits and it
can also run them and return the result.

Some platforms supported are:
- cirq
- qiskit
"""

import qiskit
from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute, Aer

import cirq
from cirq.contrib.qasm_import import circuit_from_qasm

from cProfile import run
from functools import reduce
import re

from typing import List, Dict, FrozenSet, cast, Any


def convert_qasm_to_cirq_native(qasm_path: str) -> cirq.circuits.Circuit:
    """Convert qasm file path to a cirq circuit object."""
    return circuit_from_qasm(open(qasm_path, 'r').read())


def convert_qasm_to_qiskit_native(qasm_path: str) -> QuantumCircuit:
    """Convert qasm file path to a qiskit circuit object."""
    return QuantumCircuit.from_qasm_file(qasm_path)


def run_cirq(
        qc_cirq: cirq.circuits.circuit.Circuit,
        shots: int = 8192):
    """Run cirq and return the result."""
    simulator = cirq.Simulator()
    result = simulator.run(qc_cirq, repetitions=shots)
    measurement_keys = qc_cirq.all_measurement_key_names()
    register_numbers = [
        #int(re.findall(r'\[(\d+)\]', measurement_key)[0])
        int(re.search(r"\d+", measurement_key).group(0))
        for measurement_key in measurement_keys
    ]
    sorted_measurement_keys = list(zip(*sorted(zip(register_numbers, measurement_keys))))[1]
    result_dict = dict(result.multi_measurement_histogram(keys=sorted_measurement_keys))
    keys = list(map(lambda arr: reduce(lambda x, y: str(x) + str(y), arr[::-1]), result_dict.keys()))
    counts_cirq = dict(zip(keys, [value for value in result_dict.values()]))
    return counts_cirq


def run_qiskit(
        qc_qiskit: qiskit.circuit.quantumcircuit.QuantumCircuit,
        shots: int = 8192):
    """Run qiskit and return the result."""
    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc_qiskit, backend=backend, shots=shots)
    job_result = job.result()
    counts_qiskit = job_result.get_counts(qc_qiskit)
    return counts_qiskit


def execute_qiskit_and_cirq(
        qc_qiskit: qiskit.circuit.quantumcircuit.QuantumCircuit,
        qc_cirq: cirq.circuits.circuit.Circuit,
        shots: int = 8192):
    """Execute the quantum circuits and return the result dictionaries."""
    counts_qiskit = run_qiskit(qc_qiskit, shots)
    counts_cirq = run_cirq(qc_cirq, shots)
    return {"qiskit": counts_qiskit, "cirq": counts_cirq}


def convert_and_execute_qiskit_and_cirq_natively(
        qasm_path: str,
        shots: int = 8192):
    """Convert qasm file to qiskit/cirq circuits and execute them."""
    qc_qiskit = convert_qasm_to_qiskit_native(qasm_path)
    qc_cirq = convert_qasm_to_cirq_native(qasm_path)
    return execute_qiskit_and_cirq(qc_qiskit, qc_cirq, shots)
