
# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter

# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(7, name='qr')
cr = ClassicalRegister(7, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(RZZGate(2.0549471012132114), qargs=[qr[5], qr[6]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[6], qr[4], qr[1]], cargs=[])
qc.append(RYYGate(4.549715767353061), qargs=[qr[2], qr[5]], cargs=[])
qc.append(RYYGate(1.7784823832136227), qargs=[qr[0], qr[4]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[3], qr[2]], cargs=[])
qc.append(ECRGate(), qargs=[qr[6], qr[0]], cargs=[])
qc.append(RZXGate(1.7009764849793279), qargs=[qr[0], qr[6]], cargs=[])
qc.append(RYYGate(0.8783624118527082), qargs=[qr[3], qr[4]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[1], qr[0], qr[6]], cargs=[])
qc.append(HGate(), qargs=[qr[2]], cargs=[])
qc.append(YGate(), qargs=[qr[3]], cargs=[])
qc.append(RZXGate(4.626516799242062), qargs=[qr[0], qr[1]], cargs=[])
qc.append(CRXGate(3.456774343949486), qargs=[qr[3], qr[5]], cargs=[])
qc.append(RZXGate(5.750557455994805), qargs=[qr[1], qr[3]], cargs=[])
qc.append(RXGate(4.810686391845515), qargs=[qr[0]], cargs=[])
qc.append(TGate(), qargs=[qr[5]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[2], qr[5], qr[0]], cargs=[])
qc.append(SdgGate(), qargs=[qr[0]], cargs=[])
qc.append(RXGate(5.773025482276404), qargs=[qr[3]], cargs=[])
qc.append(SdgGate(), qargs=[qr[5]], cargs=[])
qc.append(CHGate(), qargs=[qr[6], qr[5]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[2], qr[1]], cargs=[])
qc.append(RXGate(0.041239490820221554), qargs=[qr[5]], cargs=[])

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
backend_e5edeb491b5e49f59d37b5d841e91f7e = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_e5edeb491b5e49f59d37b5d841e91f7e, shots=1959).result().get_counts(qc)
RESULT = counts