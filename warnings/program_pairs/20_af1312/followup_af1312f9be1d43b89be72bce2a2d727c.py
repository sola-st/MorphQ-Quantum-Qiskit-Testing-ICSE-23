# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(3, name='qr')
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')


subcircuit = QuantumCircuit(qr, cr, name='subcircuit')
subcircuit.append(CU3Gate(2.5908920801113684,1.4170233948973556,0.759407884354721), qargs=[qr[0], qr[1]], cargs=[])
subcircuit.append(CUGate(4.800402901233517,1.4478561724813444,5.73982741120932,0.9299604415696613), qargs=[qr[0], qr[1]], cargs=[])
subcircuit.append(RZXGate(5.901879518178167), qargs=[qr[1], qr[2]], cargs=[])
subcircuit.append(CSwapGate(), qargs=[qr[1], qr[0], qr[2]], cargs=[])
subcircuit.append(DCXGate(), qargs=[qr[0], qr[1]], cargs=[])
subcircuit.append(iSwapGate(), qargs=[qr[1], qr[2]], cargs=[])
subcircuit.append(CYGate(), qargs=[qr[1], qr[2]], cargs=[])
subcircuit.append(iSwapGate(), qargs=[qr[2], qr[1]], cargs=[])

qc.append(subcircuit, qargs=qr, cargs=cr)
qc.append(subcircuit.inverse(), qargs=qr, cargs=cr)
qc.append(IGate(), qargs=[qr[2]], cargs=[])
# SECTION
# NAME: MEASUREMENT

qc.measure(qr, cr)
# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3, coupling_map=None)
# SECTION
# NAME: QASM_CONVERSION

qc = QuantumCircuit.from_qasm_str(qc.qasm())
# SECTION
# NAME: EXECUTION

from qiskit import Aer, transpile, execute
backend_f400230b33464ec08c57e4b7b8f88b0c = Aer.get_backend('aer_simulator_statevector')
counts = execute(qc, backend=backend_f400230b33464ec08c57e4b7b8f88b0c, shots=489).result().get_counts(qc)
RESULT = counts
