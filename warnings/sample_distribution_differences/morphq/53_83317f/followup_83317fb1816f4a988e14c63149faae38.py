# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr_1 = QuantumRegister(10, name='qr_1')
cr_1 = ClassicalRegister(10, name='cr_1')
qc_1 = QuantumCircuit(qr_1, cr_1, name='qc_1')


qc_1.append(RZGate(6.163759533339787), qargs=[qr_1[2]], cargs=[])
qc_1.append(CRZGate(4.2641612072511235), qargs=[qr_1[5], qr_1[1]], cargs=[])
qc_1.append(CCXGate(), qargs=[qr_1[4], qr_1[8], qr_1[6]], cargs=[])
qc_1.append(ZGate(), qargs=[qr_1[1]], cargs=[])
qc_1.append(XGate(), qargs=[qr_1[6]], cargs=[])
qc_1.append(RCCXGate(), qargs=[qr_1[9], qr_1[5], qr_1[7]], cargs=[])
qc_1.append(RZGate(4.229610589867865), qargs=[qr_1[0]], cargs=[])
qc_1.append(CCXGate(), qargs=[qr_1[6], qr_1[9], qr_1[1]], cargs=[])
qc_1.append(SdgGate(), qargs=[qr_1[6]], cargs=[])
qc_1.append(U2Gate(4.214504315296764, 4.6235667602042065), qargs=[qr_1[9]],
    cargs=[])
qc_1.append(CSXGate(), qargs=[qr_1[2], qr_1[1]], cargs=[])
qc_1.append(CHGate(), qargs=[qr_1[0], qr_1[6]], cargs=[])
qc_1.append(CU1Gate(4.028174522740928), qargs=[qr_1[8], qr_1[0]], cargs=[])
qc_1.append(RZGate(5.0063780207098425), qargs=[qr_1[5]], cargs=[])
qc_1.append(U2Gate(2.5163050709890156, 2.1276323672732023), qargs=[qr_1[1]],
    cargs=[])
qc_1.append(TGate(), qargs=[qr_1[0]], cargs=[])
qc_1.append(RZZGate(3.950837470808744), qargs=[qr_1[3], qr_1[0]], cargs=[])
qc_1.append(TGate(), qargs=[qr_1[0]], cargs=[])
qc_1.append(SXdgGate(), qargs=[qr_1[4]], cargs=[])
qc_1.append(RZGate(4.722103101046168), qargs=[qr_1[1]], cargs=[])
qc_1.append(CRZGate(0.6393443962862078), qargs=[qr_1[4], qr_1[2]], cargs=[])
qc_1.append(CU1Gate(2.5476776328466872), qargs=[qr_1[2], qr_1[7]], cargs=[])
qc_1.append(RZGate(3.6614081973587154), qargs=[qr_1[5]], cargs=[])
qc_1.append(XGate(), qargs=[qr_1[7]], cargs=[])
qc_1.append(CSXGate(), qargs=[qr_1[6], qr_1[0]], cargs=[])


qr_2 = QuantumRegister(1, name='qr_2')
cr_2 = ClassicalRegister(1, name='cr_2')
qc_2 = QuantumCircuit(qr_2, cr_2, name='qc_2')


qc_2.append(ZGate(), qargs=[qr_2[0]], cargs=[])
qc_2.append(TGate(), qargs=[qr_2[0]], cargs=[])
qc_2.append(SXdgGate(), qargs=[qr_2[0]], cargs=[])
# SECTION
# NAME: MEASUREMENT

qc_1.measure(qr_1, cr_1)
qc_2.measure(qr_2, cr_2)
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc_1 = transpile(qc_1, basis_gates=None, optimization_level=0, coupling_map=None)
qc_2 = transpile(qc_2, basis_gates=None, optimization_level=0, coupling_map=None)
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_3ad599ab7b8546cabb2609ccb283d2e7 = Aer.get_backend('qasm_simulator')
counts_1 = execute(qc_1, backend=backend_3ad599ab7b8546cabb2609ccb283d2e7, shots=7838).result().get_counts(qc_1)
counts_2 = execute(qc_2, backend=backend_3ad599ab7b8546cabb2609ccb283d2e7, shots=7838).result().get_counts(qc_2)
RESULT = [counts_1, counts_2]
