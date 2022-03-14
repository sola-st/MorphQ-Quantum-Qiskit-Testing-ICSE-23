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
subcircuit = QuantumCircuit(qr, cr, name='subcircuit')
subcircuit.append(RZGate(1.032590781866799), qargs=[qr[3]], cargs=[])
subcircuit.append(XGate(), qargs=[qr[1]], cargs=[])
subcircuit.append(U3Gate(2.170588130029331, 1.4062174981752917, 2.982982851779933), qargs=[qr[7]], cargs=[])
subcircuit.append(RZXGate(3.295405625683573), qargs=[qr[7], qr[2]], cargs=[])
subcircuit.append(CUGate(4.798089518890295, 0.7427400452786052, 2.7761396078437754, 4.7034794987279165), qargs=[qr[7], qr[2]], cargs=[])
subcircuit.append(TGate(), qargs=[qr[6]], cargs=[])
subcircuit.append(RYYGate(5.768490947612604), qargs=[qr[1], qr[4]], cargs=[])
subcircuit.append(CYGate(), qargs=[qr[0], qr[1]], cargs=[])
subcircuit.append(CUGate(3.9553074840649622, 6.175732625959032, 2.3228974216682023, 3.769788816723433), qargs=[qr[5], qr[7]], cargs=[])
qc.append(subcircuit, qargs=qr, cargs=cr)
qc.append(subcircuit.inverse(), qargs=qr, cargs=cr)
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
# NAME: USELESS_ENTITIES

qr_bb77d7 = QuantumRegister(5, name='qr_bb77d7')
qc.add_register(qr_bb77d7)
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=0, coupling_map=None)
# SECTION
# NAME: QASM_CONVERSION

qc = QuantumCircuit.from_qasm_str(qc.qasm())
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_b704ab29748b469da2dc90035262bf00 = Aer.get_backend('aer_simulator_statevector_gpu')
counts = execute(qc, backend=backend_b704ab29748b469da2dc90035262bf00, shots=2771).result().get_counts(qc)
RESULT = counts
