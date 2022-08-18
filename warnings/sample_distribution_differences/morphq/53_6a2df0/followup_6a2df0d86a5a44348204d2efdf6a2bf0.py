# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: PARAMETERS

p_311c30 = Parameter('p_311c30')
p_ef6cfa = Parameter('p_ef6cfa')
p_5c92ee = Parameter('p_5c92ee')
p_f8cd13 = Parameter('p_f8cd13')
# SECTION
# NAME: CIRCUIT
qr = QuantumRegister(7, name='qr')
cr = ClassicalRegister(7, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(RZGate(p_311c30), qargs=[qr[1]], cargs=[])
qc.append(ZGate(), qargs=[qr[5]], cargs=[])
qc.append(XGate(), qargs=[qr[0]], cargs=[])
qc.append(CRXGate(p_5c92ee), qargs=[qr[2], qr[3]], cargs=[])
qc.append(C3SXGate(), qargs=[qr[5], qr[4], qr[6], qr[2]], cargs=[])
qc.append(CHGate(), qargs=[qr[1], qr[5]], cargs=[])
qc.append(C3SXGate(), qargs=[qr[4], qr[2], qr[6], qr[3]], cargs=[])
qc.append(ZGate(), qargs=[qr[2]], cargs=[])
qc.append(ECRGate(), qargs=[qr[5], qr[0]], cargs=[])
qc.append(SdgGate(), qargs=[qr[5]], cargs=[])
qc.append(RCCXGate(), qargs=[qr[2], qr[3], qr[4]], cargs=[])
qc.append(SGate(), qargs=[qr[6]], cargs=[])
qc.append(RZGate(4.229610589867865), qargs=[qr[6]], cargs=[])
qc.append(C3SXGate(), qargs=[qr[4], qr[2], qr[6], qr[0]], cargs=[])
qc.append(CU1Gate(p_f8cd13), qargs=[qr[1], qr[4]], cargs=[])
qc.append(CRXGate(p_ef6cfa), qargs=[qr[1], qr[5]], cargs=[])
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: PARAMETER_BINDING

qc = qc.bind_parameters({p_311c30: 6.163759533339787, p_ef6cfa: 5.94477504571567, p_5c92ee: 2.0099472182748075, p_f8cd13: 3.2142159669963557})
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=2, coupling_map=None)
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_833b526709d64bd4b51e9fb0269fd326 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_833b526709d64bd4b51e9fb0269fd326, shots=1959).result().get_counts(qc)
RESULT = counts
