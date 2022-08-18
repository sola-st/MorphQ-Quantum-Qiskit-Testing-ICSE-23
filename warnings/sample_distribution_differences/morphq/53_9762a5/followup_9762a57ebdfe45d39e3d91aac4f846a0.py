# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr_1 = QuantumRegister(1, name='qr_1')
cr_1 = ClassicalRegister(1, name='cr_1')
qc_1 = QuantumCircuit(qr_1, cr_1, name='qc_1')


qc_1.append(TGate(), qargs=[qr_1[0]], cargs=[])


qr_2 = QuantumRegister(7, name='qr_2')
cr_2 = ClassicalRegister(7, name='cr_2')
qc_2 = QuantumCircuit(qr_2, cr_2, name='qc_2')


qc_2.append(RZGate(6.163759533339787), qargs=[qr_2[4]], cargs=[])
qc_2.append(ZGate(), qargs=[qr_2[5]], cargs=[])
qc_2.append(XGate(), qargs=[qr_2[5]], cargs=[])
qc_2.append(CRXGate(5.987304452123941), qargs=[qr_2[0], qr_2[5]], cargs=[])
qc_2.append(CRZGate(1.0296448789776642), qargs=[qr_2[1], qr_2[5]], cargs=[])
qc_2.append(C3SXGate(), qargs=[qr_2[0], qr_2[6], qr_2[5], qr_2[3]], cargs=[])
qc_2.append(ZGate(), qargs=[qr_2[2]], cargs=[])
qc_2.append(XGate(), qargs=[qr_2[1]], cargs=[])
qc_2.append(RYYGate(1.740253089260498), qargs=[qr_2[5], qr_2[6]], cargs=[])
qc_2.append(CRZGate(4.167661441102218), qargs=[qr_2[1], qr_2[6]], cargs=[])
qc_2.append(RZGate(4.229610589867865), qargs=[qr_2[1]], cargs=[])
qc_2.append(SXGate(), qargs=[qr_2[0]], cargs=[])
qc_2.append(CU1Gate(3.2142159669963557), qargs=[qr_2[4], qr_2[0]], cargs=[])
qc_2.append(CRXGate(5.94477504571567), qargs=[qr_2[5], qr_2[4]], cargs=[])
qc_2.append(RZZGate(5.1829934776392745), qargs=[qr_2[6], qr_2[0]], cargs=[])
qc_2.append(CSXGate(), qargs=[qr_2[0], qr_2[2]], cargs=[])
qc_2.append(ZGate(), qargs=[qr_2[5]], cargs=[])
qc_2.append(RZGate(3.775592041307464), qargs=[qr_2[4]], cargs=[])
qc_2.append(CRXGate(0.7279391018916035), qargs=[qr_2[0], qr_2[3]], cargs=[])
qc_2.append(CUGate(5.03147076606842, 5.0063780207098425, 3.1562533916051736,
    4.940217775579305), qargs=[qr_2[5], qr_2[2]], cargs=[])
qc_2.append(U2Gate(2.5163050709890156, 2.1276323672732023), qargs=[qr_2[2]],
    cargs=[])
qc_2.append(TGate(), qargs=[qr_2[5]], cargs=[])
qc_2.append(SdgGate(), qargs=[qr_2[0]], cargs=[])
qc_2.append(RZZGate(3.950837470808744), qargs=[qr_2[3], qr_2[4]], cargs=[])
# SECTION
# NAME: MEASUREMENT

qc_1.measure(qr_1, cr_1)
qc_2.measure(qr_2, cr_2)
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc_1 = transpile(qc_1, basis_gates=None, optimization_level=2, coupling_map=None)
qc_2 = transpile(qc_2, basis_gates=None, optimization_level=2, coupling_map=None)
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_782ed3c8405e4dbe829cc799edec48fc = Aer.get_backend('qasm_simulator')
counts_1 = execute(qc_1, backend=backend_782ed3c8405e4dbe829cc799edec48fc, shots=2771).result().get_counts(qc_1)
counts_2 = execute(qc_2, backend=backend_782ed3c8405e4dbe829cc799edec48fc, shots=2771).result().get_counts(qc_2)
RESULT = [counts_1, counts_2]
