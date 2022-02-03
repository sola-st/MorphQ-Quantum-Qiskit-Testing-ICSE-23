import re
import numpy as np
import uuid
from typing import Dict, Any, List


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


# User for metamorphic testing


def get_n_qubits(qasm_content: str) -> int:
    m = re.search("qreg q\[(\d*)", qasm_content)
    if m:
        return int(m.group(1))
    return -1


def replace_all_reg_occurrences(qasm_content: str, start: str, end: str) -> str:
    qasm_content = qasm_content.replace(f"q[{start}]", f"q[{end}]")
    qasm_content = qasm_content.replace(f"c[{start}]", f"c[{end}]")
    return qasm_content


def scramble_qubits(qasm_content: str, qubits_mapping: Dict[int, int]):
    """Swap the qubits based on order."""
    pairs = [{"start": k, "end": v} for k, v in qubits_mapping.items()]
    triplets = [ {"tmp": uuid.uuid4().hex, **p} for p in pairs]
    print("-" * 80)
    print(qubits_mapping)
    for triplet in triplets:
        qasm_content = replace_all_reg_occurrences(
            qasm_content, start=triplet["start"], end=triplet["tmp"])
    for triplet in triplets:
        qasm_content = replace_all_reg_occurrences(
            qasm_content, start=triplet["tmp"], end=triplet["end"])
    return qasm_content


def create_random_mapping(qasm_content: str, seed: int = None) -> Dict[int, int]:
    max_qubits = get_n_qubits(qasm_content)
    if seed:
        np.random.seed(seed)
    start_qubits = np.arange(max_qubits)
    np.random.shuffle(start_qubits)
    end_qubits = np.arange(max_qubits)
    np.random.shuffle(end_qubits)
    return {f: s for f, s in zip(start_qubits, end_qubits)}


def read_str_with_mapping(bitstring: str, direct_mapping: Dict[int, int]):
    """Given a bitstring convert it to the original mapping."""
    n_bits = len(bitstring)
    return "".join([bitstring[direct_mapping[i]] for i in range(n_bits)])


def convert_result_to_mapping(result: Dict[str, int], qubits_mapping: Dict[int, int]):
    """Convert the result via the given mapping.

    because a qubit maping will make also the result scrambled thus we have
    to reverse the mapping and read the results.
    """
    return {
        read_str_with_mapping(bitstring, qubits_mapping): freq
        for bitstring, freq in result.items()
    }


qasm_content = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];
creg c[6];
// This initializes 6 quantum registers and 6 classical registers.

h q[0];
h q[1];
h q[2];
rx(3.09457993732866) q[2];
cx q[1], q[0];
cx q[2], q[1];
// The first 3 qubits are put into superposition states.
"""

qasm_content_without_qubit_0 = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[6];
creg c[6];
// This initializes 6 quantum registers and 6 classical registers.

h q[1];
h q[2];
rx(3.09457993732866) q[2];
cx q[2], q[1];
// The first 3 qubits are put into superposition states.
"""

qasm_complete = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[10];
creg c[10];
cx q[9], q[6];
ry(0.9801424781769557) q[1];
cx q[8], q[5];
ry(6.094123332392967) q[0];
rz(1.1424399624340646) q[2];
cx q[3], q[5];
ry(0.528458648415554) q[1];
ry(5.16389904909091) q[0];
barrier q;
measure q -> c;
"""

qasm_head = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[10];
creg c[10];
cx q[9], q[6];
ry(0.9801424781769557) q[1];
barrier q;
measure q -> c;"""

qasm_tail = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[10];
creg c[10];
ry(0.528458648415554) q[1];
ry(5.16389904909091) q[0];
barrier q;
measure q -> c;"""


class QasmModifier(object):

    def __init__(self, original_qasm):
        self.original_qasm = original_qasm
        self.lines = original_qasm.split("\n")
        self.lines = [l for l in self.lines if not l.strip() == ""]
        self.hidable_lines = [
            no_line
            for no_line, line in enumerate(self.lines)
            if not (
                line.startswith("OPENQASM") or
                line.startswith("include") or
                line.startswith("qreg") or
                line.startswith("creg") or
                line.startswith("//") or
                line.startswith("barrier") or
                line.startswith("measure")
            )
        ]
        self.mask_hide = np.zeros(len(self.lines), dtype=bool)
        self.registers = detect_registers(self.original_qasm)
        self._detect_qubits()
        self._trace_every_statement_to_a_register()

    def _detect_qubits(self):
        self.q_registers = [r for r in self.registers if r[0] == "qreg"]
        only_qubit_numbers = [r[2] for r in self.q_registers]
        self.number_qubits = sum(only_qubit_numbers)
        self.qubits = [
            [(r[1], i) for i in range(r[2])]
            for r in self.q_registers
        ]
        # flatten a list
        self.qubits = [item for sublist in self.qubits for item in sublist]

    def get_available_qubits(self):
        print(self.qubits)
        return list(self.qubits)

    def _trace_every_statement_to_a_register(self):
        """Map every line in the source code to a specific register-qubit."""
        qubits_2_lines = {}
        # print("Qubits: ", self.qubits)
        for (register_name, qubit_pos) in self.qubits:
            for no_line, line in enumerate(self.lines):
                if re.search(rf"\s*{register_name}\[\s*{qubit_pos}*\s*\]\s*", line) is not None:
                    vectorized_name = f"{register_name}-{qubit_pos}"
                    current_lines = qubits_2_lines.get(vectorized_name, [])
                    current_lines.append(no_line)
                    qubits_2_lines[vectorized_name] = current_lines
        # print("qubits_2_lines: ", qubits_2_lines)
        self.qubits_2_lines = qubits_2_lines

    def hide_qubit(self, register_name, qubit_pos):
        """Hide all the operations involving the passed qubit."""
        vectorized_name = f"{register_name}-{qubit_pos}"
        lines_to_hide = self.qubits_2_lines[vectorized_name]
        for line in lines_to_hide:
            self.mask_hide[line] = True

    def hide_after_line(self, line_no):
        """Hide all the operations after the passed line number."""
        if line_no < len(self.lines):
            self.mask_hide[line_no:] = True
        if self.lines[-2] == "barrier q;":
            self.mask_hide[-2] = False
        if self.lines[-1] == "measure q -> c;":
            self.mask_hide[-1] = False

    def hide_before_line(self, line_no):
        """Hide all the operations before the passed line number."""
        for i in range(line_no):
            if i in self.hidable_lines:
                self.mask_hide[i] = True

    def get_visible(self):
        new_text = "\n".join([
            line
            for no_line, line in enumerate(self.lines)
            if not self.mask_hide[no_line]
        ])
        #print(new_text)
        return new_text

    def get_available_lines(self):
        return self.hidable_lines

    def set_visible_only(self, list_visible_lines):
        # set all as hidden
        self.mask_hide = np.ones(len(self.lines), dtype=bool)
        # restore visibility for lines passed in the list
        for line_no in list_visible_lines:
            self.mask_hide[line_no] = False
        # restore the visibility for all the essential lines
        # namely those which are not hidable
        for i in range(len(self.lines)):
            if i not in self.hidable_lines:
                self.mask_hide[i] = False

    def reset_mask(self):
        self.mask_hide = np.zeros(len(self.lines), dtype=bool)


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


def test_qasm_modifier():
    qasm_modifier = QasmModifier(qasm_content)
    expected_result = list(zip([c for c in "qqqqqq"], list(range(6))))
    assert qasm_modifier.get_available_qubits() == expected_result


def test_hide():
    qasm_modifier = QasmModifier(qasm_content)
    qasm_modifier.hide_qubit("q", 0)
    expected_output = qasm_content_without_qubit_0
    assert qasm_modifier.get_visible() == expected_output


def test_hide_tail():
    qasm_modifier = QasmModifier(qasm_complete)
    qasm_modifier.hide_after_line(6)
    expected_output = qasm_head
    assert qasm_modifier.get_visible() == expected_output


def test_hide_head():
    qasm_modifier = QasmModifier(qasm_complete)
    qasm_modifier.hide_before_line(10)
    expected_output = qasm_head
    assert qasm_modifier.get_visible() == expected_output


if __name__ == "__main__":
    test_hide_tail()