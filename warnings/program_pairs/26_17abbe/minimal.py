import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit import Aer, transpile, execute

qr = QuantumRegister(3, name='qr')
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
subcircuit = QuantumCircuit(qr, name='subcircuit')
subcircuit.append(CSwapGate(), qargs=[qr[0], qr[1], qr[2]], cargs=[])
subcircuit.append(CCXGate(), qargs=[qr[0], qr[1], qr[2]], cargs=[])
qc.append(subcircuit, qargs=qr)
qc.append(subcircuit.inverse(), qargs=qr)
qc.measure(qr, cr)
qc = transpile(qc, optimization_level=3)
my_qasm = qc.qasm()
print(my_qasm)

qc = QuantumCircuit.from_qasm_str(my_qasm)