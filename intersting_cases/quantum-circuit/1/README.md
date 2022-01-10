The original file was: `bb84_n8.qasm` from Tket Bench 1 (`experiment_v06.yaml`)from the publication arxiv-2003-10611.

This is a problem which rises because the Cirq platform is not able to run the code given by the qconvert utilities.
This happens due to repeated measurement. The Cirq circuit cannot use twice the same `key` for a measurement, such as `m00`.
```python
cirq.measure(q[0], key='m00'),
...
cirq.X(q[0]),
...
cirq.measure(q[0], key='m00'),

simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=8192)
result_dict = dict(result.multi_measurement_histogram(keys=['m60', 'm00', 'm30', 'm10', 'm20', 'm40', 'm50', 'm70', 'm00', 'm50', 'm60', 'm10', 'm30', 'm70', 'm20', 'm40', ]))
keys = list(map(lambda arr: reduce(lambda x, y: str(x) + str(y), arr[::-1]), result_dict.keys()))
counts = dict(zip(keys,[value for value in result_dict.values()]))
print(counts)
```

Possible solution:
1. remove extra measurement from the qasm code.
1. change the mapping function of the qconvert utilities.

**Additional warning:**
In any case, the classical register here has the size of 8, but the register is populated twice, thus Qiskit tries to return the entire result with two measrument but for some reason the first measrumenet is `empty`. Chekck the content of execution:
```
{"0 1 0 0 0 1 0 0": 249, "0 0 0 1 0 0 0 1": 266, "0 0 0 0 0 1 0 0": 249, ... }
```