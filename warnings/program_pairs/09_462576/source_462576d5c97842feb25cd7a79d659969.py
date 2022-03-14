
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
qc.append(RC3XGate(), qargs=[qr[5], qr[4], qr[7], qr[0]], cargs=[])
qc.append(RYGate(4.577315427580833), qargs=[qr[6]], cargs=[])
qc.append(CPhaseGate(3.8958253680897545), qargs=[qr[4], qr[6]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[4]], cargs=[])
qc.append(ZGate(), qargs=[qr[7]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[6]], cargs=[])
qc.append(C4XGate(), qargs=[qr[0], qr[4], qr[2], qr[3], qr[1]], cargs=[])
qc.append(SXGate(), qargs=[qr[5]], cargs=[])
qc.append(CU3Gate(5.6334380494507,2.031963053978228,4.115588921668292), qargs=[qr[7], qr[2]], cargs=[])
qc.append(XGate(), qargs=[qr[4]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[6], qr[0]], cargs=[])
qc.append(CYGate(), qargs=[qr[7], qr[5]], cargs=[])
qc.append(RYGate(2.9525339778910276), qargs=[qr[3]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[6]], cargs=[])
qc.append(CSXGate(), qargs=[qr[4], qr[2]], cargs=[])
qc.append(XGate(), qargs=[qr[7]], cargs=[])
qc.append(PhaseGate(1.2438266115605516), qargs=[qr[7]], cargs=[])
qc.append(SXGate(), qargs=[qr[0]], cargs=[])
qc.append(UGate(1.2475578981205417,6.151167587061927,4.766205850306024), qargs=[qr[2]], cargs=[])
qc.append(UGate(6.150190310902739,2.450261504210688,5.447933987599033), qargs=[qr[3]], cargs=[])
qc.append(C3XGate(4.684182496138248), qargs=[qr[7], qr[2], qr[4], qr[3]], cargs=[])
qc.append(ZGate(), qargs=[qr[7]], cargs=[])
qc.append(CYGate(), qargs=[qr[3], qr[4]], cargs=[])
qc.append(CPhaseGate(0.14740362211632352), qargs=[qr[6], qr[7]], cargs=[])
qc.append(C4XGate(), qargs=[qr[3], qr[5], qr[0], qr[6], qr[4]], cargs=[])
qc.append(U3Gate(3.93259544543144,0.8995363765101827,0.9258326441720094), qargs=[qr[6]], cargs=[])
qc.append(UGate(3.914387676578735,1.041601853524223,3.356938865229232), qargs=[qr[2]], cargs=[])
qc.append(XGate(), qargs=[qr[5]], cargs=[])

# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)

# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=2, coupling_map=None)

# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_7e67d8ab8ef944f9ba7f1e056f79a182 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_7e67d8ab8ef944f9ba7f1e056f79a182, shots=2771).result().get_counts(qc)
RESULT = counts