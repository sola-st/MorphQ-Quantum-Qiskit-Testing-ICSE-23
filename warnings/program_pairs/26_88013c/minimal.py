import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.library.standard_gates import *
from qiskit import transpile

qr = QuantumRegister(3, name='qr') # with 2 bits it doesn't crash
cr = ClassicalRegister(3, name='cr')
qc = QuantumCircuit(qr, cr, name='qc')
subcircuit = QuantumCircuit(qr, name='subcircuit')

subcircuit.append(CXGate(), qargs=[qr[0], qr[1]], cargs=[])
subcircuit.append(CU1Gate(3), qargs=[qr[0], qr[1]], cargs=[])
qc.append(subcircuit, qargs=qr)
qc.append(subcircuit.inverse(), qargs=qr)
qc.measure(qr, cr)
qc = transpile(qc, basis_gates=None, optimization_level=3, coupling_map=None)

my_qasm = qc.qasm()
print(my_qasm)

qc = QuantumCircuit.from_qasm_str(my_qasm)