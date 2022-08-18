# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(11, name='qr')
cr = ClassicalRegister(11, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(CUGate(1.4006987211512518, 5.87171748222823, 1.6118094341214977, 3.48470543480054), qargs=[qr[0], qr[1]], cargs=[])
qc.append(RXXGate(3.4965748481666385), qargs=[qr[0], qr[9]], cargs=[])
qc.append(RYGate(1.6125723299807893), qargs=[qr[0]], cargs=[])
qc.append(C3XGate(5.748870687038669), qargs=[qr[5], qr[6], qr[2], qr[10]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[10], qr[9]], cargs=[])
qc.append(RYGate(3.4959547081113205), qargs=[qr[7]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[4], qr[2], qr[10]], cargs=[])
qc.append(CRYGate(1.9836175804480751), qargs=[qr[4], qr[7]], cargs=[])
qc.append(CU1Gate(4.388257530988808), qargs=[qr[3], qr[7]], cargs=[])
qc.append(CYGate(), qargs=[qr[6], qr[10]], cargs=[])
qc.append(RYGate(4.206888046259435), qargs=[qr[3]], cargs=[])
qc.append(CYGate(), qargs=[qr[7], qr[0]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[6], qr[1]], cargs=[])
qc.append(CU3Gate(0.9284573101905567, 0.45091656513571715, 3.783886899929776), qargs=[qr[8], qr[9]], cargs=[])
qc.append(C3XGate(3.656036398651311), qargs=[qr[9], qr[7], qr[3], qr[8]], cargs=[])
qc.append(RXXGate(1.292848801067894), qargs=[qr[8], qr[5]], cargs=[])
qc.append(CU3Gate(0.10112416585974073, 0.056282917670884815, 5.845989124786563), qargs=[qr[3], qr[1]], cargs=[])
qc.append(PhaseGate(1.0660267574256566), qargs=[qr[3]], cargs=[])
qc.append(TdgGate(), qargs=[qr[7]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[8], qr[1], qr[0], qr[6]], cargs=[])
qc.append(HGate(), qargs=[qr[2]], cargs=[])
qc.append(CXGate(), qargs=[qr[1], qr[2]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[2]], cargs=[])
qc.append(CXGate(), qargs=[qr[8], qr[2]], cargs=[])
qc.append(TGate(), qargs=[qr[2]], cargs=[])
qc.append(CXGate(), qargs=[qr[1], qr[2]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[2]], cargs=[])
qc.append(CXGate(), qargs=[qr[8], qr[2]], cargs=[])
qc.append(TGate(), qargs=[qr[2]], cargs=[])
qc.append(TGate(), qargs=[qr[1]], cargs=[])
qc.append(HGate(), qargs=[qr[2]], cargs=[])
qc.append(CXGate(), qargs=[qr[8], qr[1]], cargs=[])
qc.append(TGate().inverse(), qargs=[qr[1]], cargs=[])
qc.append(TGate(), qargs=[qr[8]], cargs=[])
qc.append(CXGate(), qargs=[qr[8], qr[1]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[3], qr[10]], cargs=[])
qc.append(CU3Gate(3.4734999646181017, 2.968368263873928, 2.645966679992045), qargs=[qr[8], qr[3]], cargs=[])
qc.append(PhaseGate(0.36976685792294617), qargs=[qr[4]], cargs=[])
qc.append(CSXGate(), qargs=[qr[7], qr[6]], cargs=[])
qc.append(CSXGate(), qargs=[qr[7], qr[5]], cargs=[])
qc.append(UGate(4.508730217184336, 0.737449305641411, 0.7704278059574924), qargs=[qr[8]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[7], qr[2], qr[4], qr[1]], cargs=[])
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
backend_6207f57798ca40c49020edcbc9b75e4e = Aer.get_backend('aer_simulator')
counts = execute(qc, backend=backend_6207f57798ca40c49020edcbc9b75e4e,
    shots=7838).result().get_counts(qc)
RESULT = counts
