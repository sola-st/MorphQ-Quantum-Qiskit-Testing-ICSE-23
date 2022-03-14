
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter

# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(8, name='qr')
cr = ClassicalRegister(8, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(ECRGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(CZGate(), qargs=[qr[3], qr[1]], cargs=[])
qc.append(CZGate(), qargs=[qr[6], qr[1]], cargs=[])
qc.append(RCCXGate(), qargs=[qr[7], qr[3], qr[4]], cargs=[])
qc.append(RYGate(2.3849837679266135), qargs=[qr[3]], cargs=[])
qc.append(TdgGate(), qargs=[qr[0]], cargs=[])
qc.append(SGate(), qargs=[qr[5]], cargs=[])
qc.append(CCXGate(), qargs=[qr[0], qr[4], qr[5]], cargs=[])
qc.append(RZXGate(1.3124468243705203), qargs=[qr[3], qr[5]], cargs=[])
qc.append(C4XGate(), qargs=[qr[0], qr[3], qr[1], qr[7], qr[5]], cargs=[])
qc.append(YGate(), qargs=[qr[4]], cargs=[])
qc.append(PhaseGate(4.67294652784929), qargs=[qr[3]], cargs=[])

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
backend_b704ab29748b469da2dc90035262bf00 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_b704ab29748b469da2dc90035262bf00, shots=2771).result().get_counts(qc)
RESULT = counts