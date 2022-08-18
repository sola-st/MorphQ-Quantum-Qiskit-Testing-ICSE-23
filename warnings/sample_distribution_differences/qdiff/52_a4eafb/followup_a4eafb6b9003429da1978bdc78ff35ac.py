# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(10, name='qr')
cr = ClassicalRegister(10, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(CUGate(1.4006987211512518, 5.87171748222823, 1.6118094341214977, 3.48470543480054), qargs=[qr[5], qr[3]], cargs=[])
qc.append(U2Gate(0.49960530614896387, 3.4965748481666385), qargs=[qr[0]], cargs=[])
qc.append(RYGate(1.6125723299807893), qargs=[qr[0]], cargs=[])
qc.append(C3XGate(5.748870687038669), qargs=[qr[9], qr[1], qr[5], qr[2]], cargs=[])
qc.append(RYGate(5.620914585085149), qargs=[qr[9]], cargs=[])
qc.append(TGate(), qargs=[qr[4]], cargs=[])
qc.append(ZGate(), qargs=[qr[7]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[4], qr[2], qr[9]], cargs=[])
qc.append(CRYGate(1.9836175804480751), qargs=[qr[6], qr[9]], cargs=[])
qc.append(CU1Gate(4.388257530988808), qargs=[qr[3], qr[6]], cargs=[])
qc.append(CYGate(), qargs=[qr[5], qr[9]], cargs=[])
qc.append(RYGate(4.206888046259435), qargs=[qr[1]], cargs=[])
qc.append(CHGate(), qargs=[qr[3], qr[0]], cargs=[])
qc.append(CU1Gate(0.4741087495581082), qargs=[qr[1], qr[6]], cargs=[])
qc.append(RXXGate(6.264256245114884), qargs=[qr[5], qr[8]], cargs=[])
qc.append(TGate(), qargs=[qr[7]], cargs=[])
qc.append(C3XGate(3.656036398651311), qargs=[qr[9], qr[7], qr[3], qr[8]], cargs=[])
qc.append(RXXGate(1.292848801067894), qargs=[qr[7], qr[5]], cargs=[])
qc.append(CU3Gate(0.10112416585974073, 0.056282917670884815, 5.845989124786563), qargs=[qr[7], qr[5]], cargs=[])
qc.append(HGate(), qargs=[qr[9]], cargs=[])
qc.append(CXGate(), qargs=[qr[6], qr[9]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[9]], cargs=[])
qc.append(CXGate(), qargs=[qr[7], qr[9]], cargs=[])
qc.append(TGate(), qargs=[qr[9]], cargs=[])
qc.append(CXGate(), qargs=[qr[6], qr[9]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[9]], cargs=[])
qc.append(CXGate(), qargs=[qr[7], qr[9]], cargs=[])
qc.append(TGate(), qargs=[qr[9]], cargs=[])
qc.append(TGate(), qargs=[qr[6]], cargs=[])
qc.append(HGate(), qargs=[qr[9]], cargs=[])
qc.append(CXGate(), qargs=[qr[7], qr[6]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[6]], cargs=[])
qc.append(TGate(), qargs=[qr[7]], cargs=[])
qc.append(CXGate(), qargs=[qr[7], qr[6]], cargs=[])
qc.append(CCXGate(), qargs=[qr[7], qr[6], qr[1]], cargs=[])
qc.append(C3XGate(0.8785184623539408), qargs=[qr[7], qr[6], qr[2], qr[5]], cargs=[])
qc.append(RZXGate(3.906832070781019), qargs=[qr[6], qr[2]], cargs=[])
qc.append(RXXGate(2.7782596144211196), qargs=[qr[2], qr[6]], cargs=[])
qc.append(CHGate(), qargs=[qr[3], qr[1]], cargs=[])
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
backend_c78d41fefbd5440f83de92ef37fbd821 = Aer.get_backend(
    'aer_simulator_matrix_product_state')
counts = execute(qc, backend=backend_c78d41fefbd5440f83de92ef37fbd821,
    shots=5542).result().get_counts(qc)
RESULT = counts
