# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(2, name='qr')
cr = ClassicalRegister(2, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(ECRGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(U1Gate(0.07645578313559849), qargs=[qr[1]], cargs=[])
qc.append(TdgGate(), qargs=[qr[0]], cargs=[])
qc.append(RYGate(3.036477369136538), qargs=[qr[1]], cargs=[])
qc.append(PhaseGate(4.881694463136383), qargs=[qr[0]], cargs=[])
subcircuit = QuantumCircuit(qr, cr, name='subcircuit')
subcircuit.append(RXXGate(5.51426247474029), qargs=[qr[0], qr[1]], cargs=[])
subcircuit.append(CZGate(), qargs=[qr[1], qr[0]], cargs=[])
subcircuit.append(U2Gate(4.797935396024987, 0.6344276815811839), qargs=[qr[0]], cargs=[])
subcircuit.append(CHGate(), qargs=[qr[0], qr[1]], cargs=[])
subcircuit.append(SXGate(), qargs=[qr[0]], cargs=[])
subcircuit.append(CU3Gate(5.440882692563118, 1.8851556969192012, 2.944117838889452), qargs=[qr[1], qr[0]], cargs=[])
subcircuit.append(CPhaseGate(3.9470867646141365), qargs=[qr[1], qr[0]], cargs=[])
subcircuit.append(CPhaseGate(0.27083605847020614), qargs=[qr[0], qr[1]], cargs=[])
subcircuit.append(ECRGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(subcircuit, qargs=qr, cargs=cr)
qc.append(subcircuit.inverse(), qargs=qr, cargs=cr)
qc.append(TGate(), qargs=[qr[0]], cargs=[])
qc.append(U1Gate(3.34149534835996), qargs=[qr[0]], cargs=[])
qc.append(RYGate(2.9059964560129927), qargs=[qr[0]], cargs=[])
qc.append(CRXGate(0.8276603226911154), qargs=[qr[0], qr[1]], cargs=[])
qc.append(CRYGate(2.7399976883191965), qargs=[qr[0], qr[1]], cargs=[])
# SECTION
# NAME: USELESS_ENTITIES

qr_8bf493 = QuantumRegister(1, name='qr_8bf493')
qc.add_register(qr_8bf493)
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: QASM_CONVERSION
qc = QuantumCircuit.from_qasm_str(qc.qasm())
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3, coupling_map=None)
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_08537e5a65ee43d982aa31974d2ef0cc = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_08537e5a65ee43d982aa31974d2ef0cc, shots=346).result().get_counts(qc)
RESULT = counts
