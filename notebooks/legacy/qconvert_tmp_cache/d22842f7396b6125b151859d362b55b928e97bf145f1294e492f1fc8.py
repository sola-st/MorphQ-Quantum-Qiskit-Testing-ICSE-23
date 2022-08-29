from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute, Aer
import numpy as np

shots = 8192

qc = QuantumCircuit()

q = QuantumRegister(14, 'q')
c = ClassicalRegister(14, 'c')

qc.add_register(q)
qc.add_register(c)

qc.ry(6.094123332392967, q[0])
qc.ry(0.9801424781769557, q[2])
qc.cx(q[13], q[9])
qc.rz(1.1424399624340646, q[2])
qc.cx(q[12], q[7])
qc.ry(0.4087312132537349, q[2])
qc.cx(q[4], q[7])
qc.rx(0.29185655071471744, q[8])
qc.rx(1.2545873742863833, q[10])
qc.rx(3.844385118274953, q[4])
qc.cx(q[4], q[5])
qc.cx(q[1], q[9])
qc.rx(3.1112882860657196, q[1])
qc.measure(q[0], c[0])
qc.measure(q[1], c[1])
qc.measure(q[2], c[2])
qc.measure(q[3], c[3])
qc.measure(q[4], c[4])
qc.measure(q[5], c[5])
qc.measure(q[6], c[6])
qc.measure(q[7], c[7])
qc.measure(q[8], c[8])
qc.measure(q[9], c[9])
qc.measure(q[10], c[10])
qc.measure(q[11], c[11])
qc.measure(q[12], c[12])
qc.measure(q[13], c[13])

backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend=backend, shots=shots)
job_result = job.result()
print(job_result.get_counts(qc))
