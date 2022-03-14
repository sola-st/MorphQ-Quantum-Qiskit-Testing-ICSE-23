# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(6, name='qr')
cr = ClassicalRegister(6, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(ECRGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(RXXGate(0.7226506013555898), qargs=[qr[1], qr[4]], cargs=[])


subcircuit = QuantumCircuit(qr, cr, name='subcircuit')
subcircuit.append(CCXGate(), qargs=[qr[0], qr[1], qr[5]], cargs=[])
subcircuit.append(C4XGate(), qargs=[qr[4], qr[0], qr[5], qr[2], qr[1]], cargs=[])
subcircuit.append(CYGate(), qargs=[qr[0], qr[2]], cargs=[])
subcircuit.append(CRZGate(2.7525044919718797), qargs=[qr[0], qr[3]], cargs=[])
subcircuit.append(RZZGate(0.6881227037382152), qargs=[qr[3], qr[4]], cargs=[])
subcircuit.append(RXXGate(2.605316968096909), qargs=[qr[3], qr[4]], cargs=[])
subcircuit.append(RZGate(1.032590781866799), qargs=[qr[0]], cargs=[])
subcircuit.append(CSwapGate(), qargs=[qr[3], qr[5], qr[2]], cargs=[])

qc.append(subcircuit, qargs=qr, cargs=cr)
qc.append(subcircuit.inverse(), qargs=qr, cargs=cr)
qc.append(YGate(), qargs=[qr[4]], cargs=[])
qc.append(RZXGate(2.9059964560129927), qargs=[qr[5], qr[4]], cargs=[])
qc.append(RCCXGate(), qargs=[qr[0], qr[2], qr[3]], cargs=[])
qc.append(RZXGate(1.7133393609362295), qargs=[qr[5], qr[3]], cargs=[])
qc.append(TdgGate(), qargs=[qr[2]], cargs=[])
qc.append(RCCXGate(), qargs=[qr[2], qr[0], qr[1]], cargs=[])
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=0, coupling_map=None)
# SECTION
# NAME: QASM_CONVERSION

qc = QuantumCircuit.from_qasm_str(qc.qasm())
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_470cddb0eb3a48219af00ff25a648093 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_470cddb0eb3a48219af00ff25a648093, shots=1385).result().get_counts(qc)
RESULT = counts
