
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter

# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(5, name='qr')
cr = ClassicalRegister(5, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(DCXGate(), qargs=[qr[4], qr[0]], cargs=[])
qc.append(IGate(), qargs=[qr[0]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[1], qr[2]], cargs=[])
qc.append(UGate(2.375674468673331,2.2043846769824382,5.896558717917478), qargs=[qr[4]], cargs=[])
qc.append(XGate(), qargs=[qr[0]], cargs=[])
qc.append(SwapGate(), qargs=[qr[3], qr[4]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[1], qr[0], qr[2], qr[3]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[2], qr[4], qr[0], qr[3]], cargs=[])
qc.append(HGate(), qargs=[qr[2]], cargs=[])
qc.append(SwapGate(), qargs=[qr[2], qr[4]], cargs=[])
qc.append(SwapGate(), qargs=[qr[3], qr[4]], cargs=[])
qc.append(C4XGate(), qargs=[qr[4], qr[1], qr[3], qr[0], qr[2]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[4], qr[2]], cargs=[])
qc.append(CUGate(4.37120701025599,4.929851961398776,2.4069172336996973,3.948289941903436), qargs=[qr[3], qr[4]], cargs=[])
qc.append(DCXGate(), qargs=[qr[1], qr[2]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[4], qr[0]], cargs=[])
qc.append(SXGate(), qargs=[qr[1]], cargs=[])
qc.append(U1Gate(2.681117808123235), qargs=[qr[4]], cargs=[])
qc.append(XGate(), qargs=[qr[3]], cargs=[])
qc.append(SXGate(), qargs=[qr[1]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[0], qr[4], qr[3], qr[1]], cargs=[])
qc.append(UGate(2.925170342046933,5.550025413995489,5.776183779078196), qargs=[qr[0]], cargs=[])
qc.append(RYYGate(4.22361731966884), qargs=[qr[4], qr[2]], cargs=[])
qc.append(UGate(4.412485255597243,2.1861059325825445,3.949110990184828), qargs=[qr[0]], cargs=[])
qc.append(RXGate(3.7441345138571434), qargs=[qr[3]], cargs=[])
qc.append(CRZGate(2.265892099322756), qargs=[qr[2], qr[4]], cargs=[])

# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3, coupling_map=None)

# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_5f6c7aeab19b4d3f932c37c1e30db0b8 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_5f6c7aeab19b4d3f932c37c1e30db0b8, shots=979).result().get_counts(qc)
RESULT = counts