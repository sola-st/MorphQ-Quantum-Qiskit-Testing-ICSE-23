
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
qc.append(U2Gate(3.415897662220728,5.44770708344405), qargs=[qr[0]], cargs=[])
qc.append(CZGate(), qargs=[qr[1], qr[0]], cargs=[])
qc.append(CRYGate(5.2397223969424696), qargs=[qr[1], qr[0]], cargs=[])
qc.append(PhaseGate(6.194811553306018), qargs=[qr[0]], cargs=[])
qc.append(CYGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(RYGate(4.316902573706935), qargs=[qr[0]], cargs=[])
qc.append(U3Gate(2.2111768876392035,1.4334789333941462,0.2666520403392416), qargs=[qr[0]], cargs=[])
qc.append(RZZGate(1.5845628804907743), qargs=[qr[0], qr[1]], cargs=[])
qc.append(CRYGate(1.5521894416184887), qargs=[qr[0], qr[1]], cargs=[])

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
backend_fb99627368d445628367a62e611bd452 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_fb99627368d445628367a62e611bd452, shots=346).result().get_counts(qc)
RESULT = counts