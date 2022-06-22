# SECTION
# NAME: PROLOGUE

import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit.circuit import Parameter
# SECTION
# NAME: CIRCUIT

qr = QuantumRegister(9, name='qr')
cr = ClassicalRegister(9, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
qc.append(DCXGate(), qargs=[qr[6], qr[7]], cargs=[])
qc.append(SXdgGate(), qargs=[qr[3]], cargs=[])
qc.append(CZGate(), qargs=[qr[4], qr[0]], cargs=[])
qc.append(XGate(), qargs=[qr[8]], cargs=[])
qc.append(RC3XGate(), qargs=[qr[7], qr[8], qr[5], qr[4]], cargs=[])
qc.append(SwapGate(), qargs=[qr[8], qr[0]], cargs=[])
qc.append(RXGate(0.31917762940267036), qargs=[qr[7]], cargs=[])
qc.append(CUGate(4.37120701025599, 4.929851961398776, 2.4069172336996973, 3.948289941903436), qargs=[qr[5], qr[2]], cargs=[])
qc.append(iSwapGate(), qargs=[qr[3], qr[1]], cargs=[])
subcircuit = QuantumCircuit(qr, cr, name='subcircuit')
subcircuit.append(SGate(), qargs=[qr[4]], cargs=[])
subcircuit.append(UGate(1.8609102394921573, 0.035493340580050464, 2.609969110637283), qargs=[qr[4]], cargs=[])
subcircuit.append(CU1Gate(3.5178540411067423), qargs=[qr[7], qr[4]], cargs=[])
subcircuit.append(HGate(), qargs=[qr[7]], cargs=[])
subcircuit.append(CRZGate(2.7787017116662835), qargs=[qr[7], qr[2]], cargs=[])
subcircuit.append(CXGate(), qargs=[qr[5], qr[1]], cargs=[])
subcircuit.append(CU1Gate(3.5793898864882667), qargs=[qr[5], qr[1]], cargs=[])
subcircuit.append(iSwapGate(), qargs=[qr[4], qr[6]], cargs=[])
subcircuit.append(RZZGate(4.858158841686378), qargs=[qr[7], qr[0]], cargs=[])
qc.append(subcircuit, qargs=qr, cargs=cr)
qc.append(subcircuit.inverse(), qargs=qr, cargs=cr)
qc.append(C4XGate(), qargs=[qr[0], qr[6], qr[4], qr[5], qr[2]], cargs=[])
qc.append(U3Gate(6.159830616557135, 5.814130909921563, 1.581219984490172), qargs=[qr[0]], cargs=[])
qc.append(IGate(), qargs=[qr[6]], cargs=[])
qc.append(UGate(6.220010921763897, 4.8804040068733645, 4.412485255597243), qargs=[qr[0]], cargs=[])
qc.append(RXGate(3.7441345138571434), qargs=[qr[3]], cargs=[])
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
backend_b1cc8872003e481787e63fe63bde0133 = Aer.get_backend('qasm_simulator')
counts = execute(qc, backend=backend_b1cc8872003e481787e63fe63bde0133, shots=3919).result().get_counts(qc)
RESULT = counts
