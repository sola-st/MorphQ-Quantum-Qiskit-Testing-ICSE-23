
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
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_470cddb0eb3a48219af00ff25a648093 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_470cddb0eb3a48219af00ff25a648093, shots=1385).result().get_counts(qc)
RESULT = counts