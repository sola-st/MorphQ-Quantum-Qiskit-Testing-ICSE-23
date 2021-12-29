import cirq
import numpy as np
from functools import reduce

q = [cirq.NamedQubit('q' + str(i)) for i in range(8)]

circuit = cirq.Circuit(
    cirq.X(q[0]),
    cirq.H(q[1]),
    cirq.X(q[2]),
    cirq.X(q[3]),
    cirq.X(q[4]),
    cirq.X(q[5]),
    cirq.H(q[7]),
    cirq.measure(q[6], key='m60'),
    cirq.H(q[1]),
    cirq.H(q[2]),
    cirq.H(q[4]),
    cirq.H(q[5]),
    cirq.H(q[7]),
    cirq.measure(q[0], key='m00'),
    cirq.measure(q[3], key='m30'),
    cirq.measure(q[1], key='m10'),
    cirq.measure(q[2], key='m20'),
    cirq.measure(q[4], key='m40'),
    cirq.measure(q[5], key='m50'),
    cirq.measure(q[7], key='m70'),
    cirq.X(q[0]),
    cirq.H(q[1]),
    cirq.X(q[2]),
    cirq.X(q[3]),
    cirq.X(q[4]),
    cirq.H(q[5]),
    cirq.H(q[6]),
    cirq.H(q[7]),
    cirq.H(q[1]),
    cirq.H(q[2]),
    cirq.H(q[3]),
    cirq.H(q[4]),
    cirq.H(q[7]),
    cirq.measure(q[0], key='m00'),
    cirq.measure(q[5], key='m50'),
    cirq.measure(q[6], key='m60'),
    cirq.H(q[2]),
    cirq.H(q[4]),
    cirq.measure(q[1], key='m10'),
    cirq.measure(q[3], key='m30'),
    cirq.measure(q[7], key='m70'),
    cirq.measure(q[2], key='m20'),
    cirq.measure(q[4], key='m40')
)

simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=8192)
result_dict = dict(result.multi_measurement_histogram(keys=['m60', 'm00', 'm30', 'm10', 'm20', 'm40', 'm50', 'm70', 'm00', 'm50', 'm60', 'm10', 'm30', 'm70', 'm20', 'm40', ]))
keys = list(map(lambda arr: reduce(lambda x, y: str(x) + str(y), arr[::-1]), result_dict.keys()))
counts = dict(zip(keys,[value for value in result_dict.values()]))
print(counts)