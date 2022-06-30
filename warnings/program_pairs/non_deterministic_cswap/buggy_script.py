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


# SECTION
# NAME: MEASUREMENT

qc.append(CSwapGate(), qargs=[qr[3], qr[2], qr[1]], cargs=[])
qc.append(CSwapGate(), qargs=[qr[3], qr[2], qr[1]], cargs=[])
qc.measure(qr, cr)

# SECTION
# NAME: OPTIMIZATION_LEVEL

from qiskit import transpile
qc = transpile(qc, basis_gates=None, optimization_level=3, coupling_map=None)

qc_decomposed = qc#.decompose()
my_qasm = qc_decomposed.qasm()
qc = QuantumCircuit.from_qasm_str(my_qasm)
print(my_qasm)

from qiskit import Aer, transpile, execute
backend_8dfab384f53945fab40deaf20a4011b1 = Aer.get_backend('qasm_simulator', max_parallel_threads=1)
counts_failing = execute(qc, backend=backend_8dfab384f53945fab40deaf20a4011b1, max_parallel_threads=1, shots=2771).result().get_counts(qc)
print(counts_failing)