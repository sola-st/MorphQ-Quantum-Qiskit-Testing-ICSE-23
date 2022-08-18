# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(4, name='qr')
cr = ClassicalRegister(4, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(CUGate(1.4006987211512518, 5.87171748222823, 1.6118094341214977, 3.48470543480054), qargs=[qr[2], qr[1]], cargs=[])
qc.append(CUGate(1.1871631023192395, 3.1208310247400375, 4.6969093516914615, 0.17758444859871442), qargs=[qr[2], qr[0]], cargs=[])
qc.append(CRYGate(0.6970696680696589), qargs=[qr[0], qr[1]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[0], qr[3], qr[1]], cargs=[])
qc.append(RYGate(1.6125723299807893), qargs=[qr[1]], cargs=[])
qc.append(SGate(), qargs=[qr[0]], cargs=[])
qc.append(SGate(), qargs=[qr[0]], cargs=[])
qc.append(TGate(), qargs=[qr[3]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[0], qr[1], qr[2], qr[3]], cargs=[])
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
backend_670501aa519446348d306597e98111fa = Aer.get_backend(
    'aer_simulator_matrix_product_state')
counts = execute(qc, backend=backend_670501aa519446348d306597e98111fa,
    shots=692).result().get_counts(qc)
RESULT = counts
