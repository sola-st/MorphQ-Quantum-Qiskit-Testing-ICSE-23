from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute, Aer
import numpy as np

shots = 8192

qc = QuantumCircuit()

q = QuantumRegister(7, 'q')
c = ClassicalRegister(7, 'c')

qc.add_register(q)
qc.add_register(c)

qc.ry(6.094123332392967, q[0])
qc.ry(0.9801424781769557, q[1])
qc.cx(q[6], q[4])
qc.rz(1.1424399624340646, q[1])
qc.cx(q[6], q[3])
qc.cx(q[2], q[4])
qc.rx(1.2545873742863833, q[5])
qc.rx(3.844385118274953, q[2])
qc.cx(q[2], q[3])
qc.measure(q[0], c[0])
qc.measure(q[1], c[1])
qc.measure(q[2], c[2])
qc.measure(q[3], c[3])
qc.measure(q[4], c[4])
qc.measure(q[5], c[5])
qc.measure(q[6], c[6])

backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend=backend, shots=shots)
job_result = job.result()
print(job_result.get_counts(qc))
