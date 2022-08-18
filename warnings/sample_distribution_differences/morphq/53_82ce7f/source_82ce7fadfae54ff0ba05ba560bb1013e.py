
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter

# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(11, name='qr')
cr = ClassicalRegister(11, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(RZGate(6.163759533339787), qargs=[qr[3]], cargs=[])
qc.append(CRZGate(4.2641612072511235), qargs=[qr[6], qr[2]], cargs=[])
qc.append(ZGate(), qargs=[qr[1]], cargs=[])
qc.append(CCXGate(), qargs=[qr[5], qr[9], qr[7]], cargs=[])
qc.append(ZGate(), qargs=[qr[2]], cargs=[])
qc.append(XGate(), qargs=[qr[7]], cargs=[])
qc.append(RCCXGate(), qargs=[qr[10], qr[6], qr[8]], cargs=[])
qc.append(RZGate(4.229610589867865), qargs=[qr[0]], cargs=[])
qc.append(CCXGate(), qargs=[qr[7], qr[10], qr[2]], cargs=[])
qc.append(SdgGate(), qargs=[qr[7]], cargs=[])
qc.append(U2Gate(4.214504315296764,4.6235667602042065), qargs=[qr[10]], cargs=[])
qc.append(CSXGate(), qargs=[qr[3], qr[2]], cargs=[])
qc.append(CHGate(), qargs=[qr[0], qr[7]], cargs=[])
qc.append(CU1Gate(4.028174522740928), qargs=[qr[9], qr[0]], cargs=[])
qc.append(RZGate(5.0063780207098425), qargs=[qr[6]], cargs=[])
qc.append(U2Gate(2.5163050709890156,2.1276323672732023), qargs=[qr[2]], cargs=[])
qc.append(TGate(), qargs=[qr[0]], cargs=[])
qc.append(RZZGate(3.950837470808744), qargs=[qr[4], qr[0]], cargs=[])
qc.append(TGate(), qargs=[qr[0]], cargs=[])
qc.append(TGate(), qargs=[qr[1]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[5]], cargs=[])
qc.append(RZGate(4.722103101046168), qargs=[qr[2]], cargs=[])
qc.append(CRZGate(0.6393443962862078), qargs=[qr[5], qr[3]], cargs=[])
qc.append(CU1Gate(2.5476776328466872), qargs=[qr[3], qr[8]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[1]], cargs=[])
qc.append(RZGate(3.6614081973587154), qargs=[qr[6]], cargs=[])
qc.append(XGate(), qargs=[qr[8]], cargs=[])
qc.append(CSXGate(), qargs=[qr[7], qr[0]], cargs=[])
qc.append(CU1Gate(3.631024984774394), qargs=[qr[10], qr[7]], cargs=[])

# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=2, coupling_map=None)

# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_763ea32472d74753810c20d768ff2c5f = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_763ea32472d74753810c20d768ff2c5f, shots=7838).result().get_counts(qc)
RESULT = counts