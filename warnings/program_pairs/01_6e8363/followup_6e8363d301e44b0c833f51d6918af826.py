# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
# SECTION
# NAME: CIRCUIT

qr_qr = QuantumRegister(3, name='qr_qr')
cr_qr = ClassicalRegister(3, name='cr_qr')
qc = QuantumCircuit(qr_qr, cr_qr, name='qc')
qc.append(RCCXGate(), qargs=[qr_qr[1], qr_qr[0], qr_qr[2]], cargs=[])
qc.append(TGate(), qargs=[qr_qr[2]], cargs=[])
qc.append(IGate(), qargs=[qr_qr[0]], cargs=[])
qc.append(ECRGate(), qargs=[qr_qr[2], qr_qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr_qr[2]], cargs=[])
qc.append(UGate(0.9807528981981786, 2.567185003403143, 1.2508606990611186), qargs=[qr_qr[0]], cargs=[])
qc.append(CSwapGate(), qargs=[qr_qr[0], qr_qr[2], qr_qr[1]], cargs=[])
qc.append(RCCXGate(), qargs=[qr_qr[1], qr_qr[0], qr_qr[2]], cargs=[])
qc.append(ECRGate(), qargs=[qr_qr[1], qr_qr[0]], cargs=[])
qc.append(ECRGate(), qargs=[qr_qr[2], qr_qr[1]], cargs=[])
qc.append(RYYGate(4.3059217797542395), qargs=[qr_qr[0], qr_qr[2]], cargs=[])
qc.append(RXGate(1.385141564493705), qargs=[qr_qr[1]], cargs=[])
# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)
# SECTION
# NAME: OPTIMIZATION_LEVEL
from qiskit import transpile
qc = transpile(qc, basis_gates=['rx', 'ry', 'rz', 'p', 'cx'],
    optimization_level=0)
# SECTION
# NAME: MEASUREMENT

qc.measure(qr_qr, cr_qr)
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_d3ff37282d7e43d19cf389b7e5b42747 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_d3ff37282d7e43d19cf389b7e5b42747, shots=489).result().get_counts(qc)
RESULT = counts
