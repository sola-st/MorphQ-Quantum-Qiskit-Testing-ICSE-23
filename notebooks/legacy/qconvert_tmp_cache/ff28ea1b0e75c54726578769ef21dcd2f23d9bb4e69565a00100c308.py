import cirq
import numpy as np
from functools import reduce

q = [cirq.NamedQubit('q' + str(i)) for i in range(2)]

circuit = cirq.Circuit(
    cirq.CNOT(q[1], q[0]),
    cirq.ry(0.9801424781769557)(q[0]),
    cirq.CNOT(q[1], q[0]),
    cirq.ry(6.094123332392967)(q[0]),
    cirq.rz(1.1424399624340646)(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.rx(3.844385118274953)(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.ry(0.4087312132537349)(q[0]),
    cirq.rx(1.2545873742863833)(q[1]),
    cirq.rx(0.29185655071471744)(q[1]),
    cirq.CNOT(q[0], q[1]),
    cirq.rx(3.1112882860657196)(q[0]),
    cirq.CNOT(q[1], q[0]),
    cirq.ry(3.267683749398383)(q[0]),
    cirq.rz(5.622366060669442)(q[1]),
    cirq.rx(6.092079887237463)(q[0]),
    cirq.ry(0.55601478868818)(q[1]),
    cirq.CNOT(q[0], q[1]),
    cirq.CNOT(q[0], q[1]),
    cirq.CNOT(q[0], q[1]),
    cirq.CNOT(q[1], q[0]),
    cirq.CNOT(q[1], q[0]),
    cirq.measure(q[0], key='c0'),
    cirq.measure(q[1], key='c1')
)

simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=8192)
result_dict = dict(result.multi_measurement_histogram(keys=['c0', 'c1']))
keys = list(map(lambda arr: reduce(lambda x, y: str(x) + str(y), arr[::-1]), result_dict.keys()))
counts = dict(zip(keys,[value for value in result_dict.values()]))
print(counts)