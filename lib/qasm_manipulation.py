import re
from typing import List


def remove_all_measurements(qasm_program: str):
    lines = qasm_program.split("\n")
    non_measurement_lines = [
        line
        for line in lines
        if re.match(r"\s*measure\s*", line) is None
    ]
    measurement_lines = [
        line
        for line in lines
        if not re.match(r"\s*measure\s*", line) is None
    ]
    new_qasm_program = "\n".join(non_measurement_lines)
    removed_measurement_section = "\n".join(measurement_lines)
    return new_qasm_program, removed_measurement_section


def detect_registers(qasm_program: str):
    """Detect the registers in the circuit."""
    # list with circuits and their number of qubits
    # example. registers = [("qreg", "q", 5), ("creg", "c", 2)]
    registers = list(zip(
        re.findall(r"\s*([c|q]reg)\s*[a-zA-Z]+\[\d+\]\s*;", qasm_program),
        re.findall(r"\s*[c|q]reg\s*([a-zA-Z]+)\[\d+\]\s*;", qasm_program),
        [
            int(e) for e in
            re.findall(r"\s*[c|q]reg\s*[a-zA-Z]+\[(\d+)\]\s*;", qasm_program)
        ]
    ))
    return registers


def get_first_and_only_quantum_register(qasm_program: str):
    """Get the first and only quantum register.

    Format: (qreg|creq, name, number_of_qubits)
    """
    quantum_registers = [
        reg
        for reg in detect_registers(qasm_program)
        if reg[0] == "qreg"
    ]
    if len(quantum_registers) != 1:
        raise ValueError("Only one quantum register is supported.")
    first_reg = {
        "type": quantum_registers[0][0],
        "name": quantum_registers[0][1],
        "n_qubits": quantum_registers[0][2]
    }
    return first_reg


def append_1Q_gate(qasm_program: str, gate: str, qubits: List[int]):
    """Append the given gate to all the qubits in the list."""
    first_qreg = get_first_and_only_quantum_register(qasm_program)
    new_qasm_program = qasm_program
    for qubit in qubits:
        new_qasm_program += "\n" + gate + " " + first_qreg["name"] + "[" + str(qubit) + "];"
    # not gate: "x q[0];"
    return new_qasm_program


qasm_content = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];
creg c[6];
// This initializes 6 quantum registers and 6 classical registers.

h q[0];
h q[1];
h q[2];
// The first 3 qubits are put into superposition states.
"""


def test_detect_registers():
    assert detect_registers(qasm_content) == [
        ('qreg', 'q', 6), ('creg', 'c', 6)
        ]


def test_append_1Q_gate():
    new_qasm = append_1Q_gate(qasm_content, "x", list(range(6)))
    lines = new_qasm.split("\n")
    for i in range(1, 7):
        c_line = lines[-i]
        assert c_line == "x q[" + str(6-i) + "];", c_line


if __name__ == "__main__":
    test_detect_registers()
    test_append_1Q_gate()