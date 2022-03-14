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


qr_0 = QuantumRegister(3, name='qr_0')
cr_0 = ClassicalRegister(3, name='cr_0')
qc_0 = QuantumCircuit(qr_0, cr_0, name='qc_0')

qc_0.append(CHGate(), qargs=[qr_0[0], qr_0[2]], cargs=[])
qc_0.append(DCXGate(), qargs=[qr_0[1], qr_0[0]], cargs=[])
qc_0.append(CSwapGate(), qargs=[qr_0[0], qr_0[1], qr_0[2]], cargs=[])
qc_0.append(SwapGate(), qargs=[qr_0[0], qr_0[2]], cargs=[])
qc_0.append(SwapGate(), qargs=[qr_0[0], qr_0[2]], cargs=[])
qc_0.append(U3Gate(3.1333796742925704, 2.0782915724294266, 
    3.8528667493673407), qargs=[qr_0[0]], cargs=[])
qc_0.append(XGate(), qargs=[qr_0[0]], cargs=[])
qc_0.append(XGate(), qargs=[qr_0[1]], cargs=[])
qc_0.append(UGate(3.2932004434738897, 4.615954301356511, 5.807945035399611),
    qargs=[qr_0[0]], cargs=[])
qc_0.append(CCXGate(), qargs=[qr_0[1], qr_0[2], qr_0[0]], cargs=[])
qc_0.append(CU3Gate(0.9780797026556811, 2.5266379849635308, 
    5.799484270194845), qargs=[qr_0[2], qr_0[1]], cargs=[])

qr_1 = QuantumRegister(3, name='qr_1')
cr_1 = ClassicalRegister(3, name='cr_1')
qc_1 = QuantumCircuit(qr_1, cr_1, name='qc_1')

qc_1.append(SwapGate(), qargs=[qr_1[0], qr_1[1]], cargs=[])
qc_1.append(SwapGate(), qargs=[qr_1[1], qr_1[2]], cargs=[])
qc_1.append(CHGate(), qargs=[qr_1[0], qr_1[1]], cargs=[])
qc_1.append(CRZGate(6.101795211804666), qargs=[qr_1[1], qr_1[2]], cargs=[])
qc_1.append(U3Gate(2.5199573414643814, 6.119039916799916, 3.381561021165288
    ), qargs=[qr_1[0]], cargs=[])
qc_1.append(UGate(3.731686677882394, 4.537227390583343, 0.42149888050188145
    ), qargs=[qr_1[1]], cargs=[])
qc_1.append(SwapGate(), qargs=[qr_1[0], qr_1[1]], cargs=[])
qc_1.append(RZZGate(1.2549960087029204), qargs=[qr_1[1], qr_1[0]], cargs=[])
# SECTION
# NAME: OPTIMIZATION_PASSES

from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import *
passmanager = PassManager()
qc = passmanager.run(qc)

passmanager = PassManager()
passmanager.append(Optimize1qGatesDecomposition(**{'basis': ['u1', 'rx']}))
passmanager.append(OptimizeSwapBeforeMeasure(**{}))
qc_0 = passmanager.run(qc_0)

passmanager = PassManager()
passmanager.append(HoareOptimizer(**{'size': 0}))
passmanager.append(CommutationAnalysis())
passmanager.append(CommutativeCancellation(**{'basis_gates': ['cx', 'p', 'sx']}))
qc_1 = passmanager.run(qc_1)
qc.append(qc_0, qargs=qr, cargs=cr)
qc.append(qc_1, qargs=qr, cargs=cr)
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=2, coupling_map=None)
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_98ae9f2e9e3f4728a9fa5a427cf0751b = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_98ae9f2e9e3f4728a9fa5a427cf0751b, shots=489).result().get_counts(qc)
RESULT = counts
