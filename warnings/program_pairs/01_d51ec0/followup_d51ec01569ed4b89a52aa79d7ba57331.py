# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
# SECTION
# NAME: CIRCUIT

qr_qr = QuantumRegister(11, name='qr_qr')
cr_qr = ClassicalRegister(11, name='cr_qr')
qc = QuantumCircuit(qr_qr, cr_qr, name='qc')
qc.append(CCXGate(), qargs=[qr_qr[10], qr_qr[0], qr_qr[9]], cargs=[])
qc.append(RXXGate(1.214286075933729), qargs=[qr_qr[2], qr_qr[4]], cargs=[])
qc.append(RZZGate(1.5279295607940084), qargs=[qr_qr[2], qr_qr[8]], cargs=[])
qc.append(SwapGate(), qargs=[qr_qr[4], qr_qr[0]], cargs=[])
qc.append(SdgGate(), qargs=[qr_qr[6]], cargs=[])
# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)
# SECTION
# NAME: OPTIMIZATION_LEVEL
from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3)
# SECTION
# NAME: MEASUREMENT

qc.measure(qr_qr, cr_qr)
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_6b172cc212eb423a8286969be00ac37f = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_6b172cc212eb423a8286969be00ac37f, shots=7838).result().get_counts(qc)
RESULT = counts
