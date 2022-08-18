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
qc.append(CUGate(1.4006987211512518, 5.87171748222823, 1.6118094341214977, 3.48470543480054), qargs=[qr[4], qr[3]], cargs=[])
qc.append(RZGate(3.1208310247400375), qargs=[qr[6]], cargs=[])
qc.append(RZGate(1.7510965512636645), qargs=[qr[6]], cargs=[])
qc.append(UGate(1.4424895697923088, 5.472664875176172, 2.66053590714238), qargs=[qr[0]], cargs=[])
qc.append(C3XGate(5.748870687038669), qargs=[qr[1], qr[2], qr[6], qr[5]], cargs=[])
qc.append(HGate(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[6], qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[6], qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr[0]], cargs=[])
qc.append(HGate(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[6], qr[0]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[0]], cargs=[])
qc.append(TGate(), qargs=[qr[6]], cargs=[])
qc.append(CXGate(), qargs=[qr[6], qr[0]], cargs=[])
qc.append(CHGate(), qargs=[qr[1], qr[6]], cargs=[])
qc.append(RXXGate(1.3311670849927728), qargs=[qr[6], qr[2]], cargs=[])
qc.append(RYGate(5.99120670299654), qargs=[qr[3]], cargs=[])
qc.append(CUGate(5.709276284014425, 1.1243723913896708, 5.481400346001526, 3.157375188814291), qargs=[qr[0], qr[6]], cargs=[])
qc.append(CSXGate(), qargs=[qr[2], qr[0]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[4], qr[3], qr[1]], cargs=[])
qc.append(CU1Gate(4.388257530988808), qargs=[qr[3], qr[4]], cargs=[])
qc.append(CUGate(2.945697832726557, 3.322311684185455, 2.468007457013939, 1.7221796439586554), qargs=[qr[6], qr[3]], cargs=[])
qc.append(RYGate(4.206888046259435), qargs=[qr[1]], cargs=[])
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
backend_1a583ba744444883999ce16846410d18 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_1a583ba744444883999ce16846410d18, shots=1959).result().get_counts(qc)
RESULT = counts
