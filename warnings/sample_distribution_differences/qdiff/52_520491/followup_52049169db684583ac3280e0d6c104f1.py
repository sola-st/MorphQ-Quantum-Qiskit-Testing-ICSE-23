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
qc.append(CUGate(1.4006987211512518, 5.87171748222823, 1.6118094341214977, 3.48470543480054), qargs=[qr[4], qr[5]], cargs=[])
qc.append(U2Gate(0.49960530614896387, 3.4965748481666385), qargs=[qr[0]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[7], qr[1], qr[0]], cargs=[])
qc.append(UGate(1.4424895697923088, 5.472664875176172, 2.66053590714238), qargs=[qr[0]], cargs=[])
qc.append(C3XGate(5.748870687038669), qargs=[qr[1], qr[7], qr[2], qr[6]], cargs=[])
qc.append(HGate(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[7], qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[0], qr[1]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[7], qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr[0]], cargs=[])
qc.append(HGate(), qargs=[qr[1]], cargs=[])
qc.append(CXGate(), qargs=[qr[7], qr[0]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[0]], cargs=[])
qc.append(TGate(), qargs=[qr[7]], cargs=[])
qc.append(CXGate(), qargs=[qr[7], qr[0]], cargs=[])
qc.append(CHGate(), qargs=[qr[1], qr[0]], cargs=[])
qc.append(RYGate(3.4959547081113205), qargs=[qr[4]], cargs=[])
qc.append(RZGate(5.264688008730697), qargs=[qr[3]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[7], qr[5], qr[4]], cargs=[])
qc.append(CCXGate(), qargs=[qr[2], qr[0], qr[5]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[4], qr[7], qr[3]], cargs=[])
qc.append(CHGate(), qargs=[qr[3], qr[4]], cargs=[])
qc.append(CUGate(2.945697832726557, 3.322311684185455, 2.468007457013939, 1.7221796439586554), qargs=[qr[7], qr[6]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[1], qr[6], qr[5], qr[0]], cargs=[])
qc.append(CHGate(), qargs=[qr[7], qr[0]], cargs=[])
qc.append(C3XGate(2.178749674182195), qargs=[qr[4], qr[3], qr[1], qr[0]], cargs=[])
qc.append(UGate(4.571498323975378, 0.08752827907617249, 4.134859538498545), qargs=[qr[1]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[4], qr[3], qr[0], qr[6]], cargs=[])
qc.append(RXXGate(1.4895817613653266), qargs=[qr[3], qr[1]], cargs=[])
qc.append(C3XGate(3.656036398651311), qargs=[qr[3], qr[6], qr[7], qr[5]], cargs=[])
qc.append(U2Gate(5.474651151291477, 2.9572626913790563), qargs=[qr[4]], cargs=[])
qc.append(UGate(3.0091570055418737, 1.8424506696221552, 6.019171707548773), qargs=[qr[6]], cargs=[])
qc.append(CU1Gate(5.118040752270066), qargs=[qr[5], qr[3]], cargs=[])
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
backend_55f5ef1c55df4ef992079534811a3759 = Aer.get_backend(
    'aer_simulator_density_matrix')
counts = execute(qc, backend=backend_55f5ef1c55df4ef992079534811a3759,
    shots=2771).result().get_counts(qc)
RESULT = counts
