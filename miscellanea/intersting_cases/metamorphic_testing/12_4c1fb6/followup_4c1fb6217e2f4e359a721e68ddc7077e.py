# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(5, name='qr')
cr = ClassicalRegister(5, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')


subcircuit = QuantumCircuit(qr, cr, name='subcircuit')
subcircuit.append(CUGate(4.638295177215426,2.4816698430762214,3.735145493818512,5.552501004888056), qargs=[qr[0], qr[4]], cargs=[])
subcircuit.append(CXGate(), qargs=[qr[2], qr[4]], cargs=[])
subcircuit.append(CSwapGate(), qargs=[qr[0], qr[2], qr[3]], cargs=[])

qc.append(subcircuit, qargs=qr, cargs=cr)
qc.append(subcircuit.inverse(), qargs=qr, cargs=cr)
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3, coupling_map=[[0, 1], [1, 0], [1, 3], [1, 4], [2, 3], [3, 1], [3, 2], [4, 1], [4, 6], [5, 6], [6, 4], [6, 5]])
# SECTION
# NAME: QASM_CONVERSION

qc = QuantumCircuit.from_qasm_str(qc.qasm())
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_04ca3b30d0b44cff8ee7c7aabe5dd837 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_04ca3b30d0b44cff8ee7c7aabe5dd837, shots=979).result().get_counts(qc)
RESULT = counts
