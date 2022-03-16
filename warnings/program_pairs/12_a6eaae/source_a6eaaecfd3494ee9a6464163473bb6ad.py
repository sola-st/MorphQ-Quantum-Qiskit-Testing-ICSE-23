
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
qc.append(TGate(), qargs=[qr[0]], cargs=[])
qc.append(U1Gate(3.34149534835996), qargs=[qr[0]], cargs=[])
qc.append(RYGate(2.9059964560129927), qargs=[qr[0]], cargs=[])
qc.append(CRXGate(0.8276603226911154), qargs=[qr[0], qr[1]], cargs=[])
qc.append(CRYGate(2.7399976883191965), qargs=[qr[0], qr[1]], cargs=[])

# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=0, coupling_map=None)

# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_08537e5a65ee43d982aa31974d2ef0cc = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_08537e5a65ee43d982aa31974d2ef0cc, shots=346).result().get_counts(qc)
RESULT = counts