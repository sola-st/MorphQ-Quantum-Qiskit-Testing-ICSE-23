
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
qc.append(CHGate(), qargs=[qr[3], qr[1]], cargs=[])
qc.append(CU1Gate(3.001459306379496), qargs=[qr[10], qr[5]], cargs=[])
qc.append(CZGate(), qargs=[qr[10], qr[2]], cargs=[])
qc.append(U1Gate(6.168334007761457), qargs=[qr[7]], cargs=[])
qc.append(CHGate(), qargs=[qr[4], qr[7]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[6]], cargs=[])
qc.append(SwapGate(), qargs=[qr[10], qr[6]], cargs=[])
qc.append(RCCXGate(), qargs=[qr[6], qr[5], qr[8]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[8], qr[7], qr[9], qr[4]], cargs=[])
qc.append(CHGate(), qargs=[qr[6], qr[8]], cargs=[])
qc.append(RCCXGate(), qargs=[qr[4], qr[2], qr[5]], cargs=[])
qc.append(RXXGate(3.717624460789032), qargs=[qr[9], qr[2]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[5]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[10]], cargs=[])
qc.append(PhaseGate(2.9363663072501205), qargs=[qr[8]], cargs=[])
qc.append(CHGate(), qargs=[qr[8], qr[10]], cargs=[])
qc.append(SwapGate(), qargs=[qr[6], qr[7]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[2], qr[8], qr[10], qr[1]], cargs=[])
qc.append(U1Gate(3.392515329500051), qargs=[qr[0]], cargs=[])
qc.append(RCCXGate(), qargs=[qr[8], qr[7], qr[6]], cargs=[])
qc.append(PhaseGate(3.491399104775617), qargs=[qr[4]], cargs=[])
qc.append(RXXGate(0.7638624774750333), qargs=[qr[10], qr[1]], cargs=[])
qc.append(RZGate(5.708541902391605), qargs=[qr[10]], cargs=[])
qc.append(RYYGate(3.955007888884436), qargs=[qr[3], qr[5]], cargs=[])
qc.append(UGate(0.7492203571871445,1.5804353903693034,0.4083158171844422), qargs=[qr[9]], cargs=[])
qc.append(CRYGate(0.0059405938354801565), qargs=[qr[10], qr[0]], cargs=[])

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
backend_8b530f83bade4c33b9ef3e11942d73d7 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_8b530f83bade4c33b9ef3e11942d73d7, shots=7838).result().get_counts(qc)
RESULT = counts