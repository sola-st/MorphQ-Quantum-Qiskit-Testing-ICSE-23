import cirq
import numpy as np
from functools import reduce

q = [cirq.NamedQubit('q' + str(i)) for i in range(14)]

circuit = cirq.Circuit(
    cirq.ry(6.094123332392967)(q[0]),
    cirq.ry(0.9801424781769557)(q[2]),
    cirq.CNOT(q[13], q[9]),
    cirq.rz(1.1424399624340646)(q[2]),
    cirq.CNOT(q[12], q[7]),
    cirq.ry(0.4087312132537349)(q[2]),
    cirq.CNOT(q[4], q[7]),
    cirq.rx(0.29185655071471744)(q[8]),
    cirq.rx(1.2545873742863833)(q[10]),
    cirq.rx(3.844385118274953)(q[4]),
    cirq.CNOT(q[4], q[5]),
    cirq.CNOT(q[1], q[9]),
    cirq.rx(3.1112882860657196)(q[1]),
    cirq.measure(q[0], key='c0'),
    cirq.measure(q[1], key='c1'),
    cirq.measure(q[2], key='c2'),
    cirq.measure(q[3], key='c3'),
    cirq.measure(q[4], key='c4'),
    cirq.measure(q[5], key='c5'),
    cirq.measure(q[6], key='c6'),
    cirq.measure(q[7], key='c7'),
    cirq.measure(q[8], key='c8'),
    cirq.measure(q[9], key='c9'),
    cirq.measure(q[10], key='c10'),
    cirq.measure(q[11], key='c11'),
    cirq.measure(q[12], key='c12'),
    cirq.measure(q[13], key='c13')
)

simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=8192)
result_dict = dict(result.multi_measurement_histogram(keys=['c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11', 'c12', 'c13']))
keys = list(map(lambda arr: reduce(lambda x, y: str(x) + str(y), arr[::-1]), result_dict.keys()))
counts = dict(zip(keys,[value for value in result_dict.values()]))
print(counts)