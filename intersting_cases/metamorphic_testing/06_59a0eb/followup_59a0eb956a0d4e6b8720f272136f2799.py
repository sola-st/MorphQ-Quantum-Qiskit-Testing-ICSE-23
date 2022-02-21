# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(3, name='qr')
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')


subcircuit = QuantumCircuit(qr, cr, name='subcircuit')
subcircuit.append(CSwapGate(), qargs=[qr[1], qr[0], qr[2]], cargs=[])
subcircuit.append(CYGate(), qargs=[qr[2], qr[1]], cargs=[])
subcircuit.append(XGate(), qargs=[qr[0]], cargs=[])
subcircuit.append(CRYGate(1.3065360008838949), qargs=[qr[2], qr[0]], cargs=[])
subcircuit.append(PhaseGate(4.870303166855185), qargs=[qr[0]], cargs=[])
subcircuit.append(UGate(3.756716362028796,5.792306648564669,0.55601478868818), qargs=[qr[0]], cargs=[])

qc.append(subcircuit, qargs=qr, cargs=cr)
qc.append(subcircuit.inverse(), qargs=qr, cargs=cr)
# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=['rx', 'ry', 'rz', 'p', 'cx'], optimization_level=3, coupling_map=[[0, 1], [1, 0], [1, 2], [2, 1]])
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_c8226e206fc345f38b3d5252915e6418 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_c8226e206fc345f38b3d5252915e6418, shots=489).result().get_counts(qc)
RESULT = counts
