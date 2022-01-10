The original file was `seca_n11.qasm` from QasmMid (`experiment_v06.yaml`).

THis problem rises because Cirq return as result only the qubits which are measured in the QASM code, whereas Qiskit measures automatically and reports as result all the qubits in the program.

Cirq result:
```json
{"101": 2018, "111": 2062, "100": 2048, "110": 2064}
```

Qiskit result:
```json
{"11000000000": 2072, "11000000001": 2111, "10000000000": 1976, "10000000001": 2033}
```