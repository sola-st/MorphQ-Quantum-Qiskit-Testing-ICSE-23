from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute, Aer
import numpy as np

shots = 8192

qc = QuantumCircuit()

q = QuantumRegister(19, 'q')
c = ClassicalRegister(19, 'c')

qc.add_register(q)
qc.add_register(c)

qc.rx(6.209957416856063, q[0])
qc.rx(2.5009858166994063, q[1])
qc.rz(1.1023958963447806, q[3])
qc.rz(1.220338852225453, q[4])
qc.ry(1.4253497199469332, q[5])
qc.rx(2.6584562936267786, q[13])
qc.cx(q[16], q[17])
qc.ry(5.562672506903891, q[1])
qc.cx(q[6], q[14])
qc.rx(3.6610304181691236, q[1])
qc.rz(2.2731851653103794, q[6])
qc.rx(3.986058781630306, q[10])
qc.rz(3.839173944630678, q[13])
qc.cx(q[5], q[12])
qc.cx(q[8], q[7])
qc.rx(0.7264518012019154, q[11])
qc.rx(1.9619951281825225, q[8])
qc.cx(q[7], q[16])
qc.cx(q[5], q[8])
qc.cx(q[9], q[18])
qc.ry(0.9987729005246175, q[10])
qc.rx(0.757932261775076, q[11])
qc.ry(0.10134279452259236, q[13])
qc.ry(3.2070781312980996, q[16])
qc.rx(6.180335123765394, q[17])
qc.ry(2.236279054882737, q[18])
qc.rz(3.42476328964376, q[11])
qc.ry(0.5227295283213563, q[16])
qc.ry(3.926384502772141, q[11])
qc.ry(3.4762184199159, q[16])
qc.cx(q[13], q[5])
qc.ry(6.179648524241403, q[16])
qc.cx(q[5], q[8])
qc.ry(2.4438485325496067, q[10])
qc.rz(4.346090578542644, q[11])
qc.cx(q[7], q[4])
qc.cx(q[9], q[12])
qc.cx(q[2], q[6])
qc.rz(1.990437060666522, q[7])
qc.cx(q[3], q[15])
qc.cx(q[10], q[11])
qc.cx(q[10], q[15])
qc.cx(q[13], q[2])
qc.cx(q[8], q[3])
qc.rx(0.5863890153630625, q[10])
qc.cx(q[17], q[10])
qc.rx(4.66125737240652, q[14])
qc.cx(q[13], q[16])
qc.cx(q[14], q[5])
qc.ry(4.375052729800289, q[16])
qc.cx(q[12], q[2])
qc.cx(q[16], q[14])
qc.rx(1.2654303879527242, q[2])
qc.ry(4.509803769431953, q[3])
qc.rz(5.828135536071984, q[6])
qc.rx(4.807240544188084, q[8])
qc.rz(4.7227184666135225, q[10])
qc.cx(q[7], q[8])
qc.cx(q[10], q[17])
qc.rz(5.076425486936402, q[8])
qc.cx(q[12], q[0])
qc.ry(4.67959486945833, q[0])
qc.rx(3.4094820760621327, q[2])
qc.rz(3.0223772266213005, q[7])
qc.rz(2.675805638999381, q[9])
qc.rz(0.6448763526718408, q[10])
qc.cx(q[12], q[18])
qc.cx(q[0], q[5])
qc.ry(0.3084863697537051, q[12])
qc.cx(q[6], q[16])
qc.cx(q[7], q[18])
qc.cx(q[8], q[10])
qc.cx(q[17], q[16])
qc.cx(q[4], q[15])
qc.cx(q[9], q[18])
qc.cx(q[1], q[9])
qc.rz(2.785761429635354, q[3])
qc.rz(1.200132095552537, q[7])
qc.cx(q[5], q[10])
qc.cx(q[18], q[4])
qc.cx(q[4], q[1])
qc.cx(q[5], q[12])
qc.ry(5.476945398038951, q[18])
qc.cx(q[6], q[0])
qc.ry(2.7005968494387864, q[18])
qc.cx(q[10], q[2])
qc.ry(3.9712903823338044, q[5])
qc.cx(q[16], q[0])
qc.cx(q[14], q[0])
qc.rz(3.7478377155859253, q[2])
qc.cx(q[17], q[14])
qc.cx(q[13], q[0])
qc.rx(1.2463683827412366, q[17])
qc.rx(0.25562002474463424, q[0])
qc.cx(q[4], q[16])
qc.ry(3.817217731464704, q[17])
qc.cx(q[7], q[9])
qc.cx(q[10], q[11])
qc.cx(q[17], q[16])
qc.cx(q[7], q[6])
qc.rx(0.022193536044990175, q[9])
qc.cx(q[10], q[12])
qc.ry(3.6487287300850766, q[17])
qc.rz(2.1963893878289524, q[6])
qc.cx(q[14], q[6])
qc.cx(q[12], q[4])
qc.cx(q[6], q[5])
qc.cx(q[5], q[2])
qc.cx(q[11], q[6])
qc.rx(4.253124951713993, q[3])
qc.rz(2.0896634641479284, q[4])
qc.cx(q[5], q[14])
qc.ry(2.957424628494065, q[3])
qc.rx(2.264609018430567, q[5])
qc.rx(3.4116991404512915, q[6])
qc.cx(q[14], q[13])
qc.cx(q[15], q[8])
qc.rz(0.03787432257016015, q[12])
qc.cx(q[6], q[17])
qc.cx(q[8], q[3])
qc.rz(1.7580479311548234, q[8])
qc.cx(q[13], q[8])
qc.cx(q[17], q[11])
qc.cx(q[11], q[3])
qc.cx(q[4], q[1])
qc.rx(5.970607048758013, q[5])
qc.cx(q[6], q[16])
qc.rz(6.10787341155158, q[6])
qc.cx(q[5], q[8])
qc.cx(q[18], q[1])
qc.ry(2.661042382655093, q[8])
qc.cx(q[16], q[5])
qc.cx(q[9], q[1])
qc.cx(q[17], q[15])
qc.cx(q[15], q[7])
qc.rx(4.097603637836061, q[16])
qc.ry(1.5402009312392198, q[17])
qc.cx(q[0], q[13])
qc.ry(1.8491850761067763, q[0])
qc.cx(q[14], q[2])
qc.ry(3.433628959633069, q[0])
qc.cx(q[11], q[4])
qc.ry(1.7431061493779807, q[6])
qc.cx(q[14], q[4])
qc.rx(5.092606239709339, q[5])
qc.cx(q[12], q[14])
qc.cx(q[11], q[18])
qc.cx(q[14], q[3])
qc.cx(q[16], q[2])
qc.cx(q[17], q[9])
qc.cx(q[6], q[11])
qc.rx(4.2168128204639945, q[13])
qc.rz(5.795499257971255, q[16])
qc.rx(2.497968607886308, q[17])
qc.cx(q[2], q[6])
qc.ry(0.8524604670728644, q[7])
qc.rz(0.21333698764615389, q[9])
qc.rx(2.5430531915056687, q[11])
qc.rz(5.01230172116195, q[6])
qc.cx(q[9], q[10])
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
qc.measure(q[14], c[14])
qc.measure(q[15], c[15])
qc.measure(q[16], c[16])
qc.measure(q[17], c[17])
qc.measure(q[18], c[18])

backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend=backend, shots=shots)
job_result = job.result()
print(job_result.get_counts(qc))
