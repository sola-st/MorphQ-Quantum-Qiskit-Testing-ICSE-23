import cirq
import numpy as np
from functools import reduce

def u3(p_theta, p_phi, p_lambda):
    return cirq.MatrixGate(np.array([[np.cos(p_theta/2), -np.exp(1j*p_lambda)*np.sin(p_theta/2)], [np.exp(1j*p_phi)*np.sin(p_theta/2), np.exp(1j*p_lambda+1j*p_phi)*np.cos(p_theta/2)]]))

q = [cirq.NamedQubit('q' + str(i)) for i in range(6)]

circuit = cirq.Circuit(
    cirq.H(q[0]),
    cirq.H(q[1]),
    cirq.H(q[2]),
    cirq.H(q[3]),
    cirq.H(q[4]),
    cirq.H(q[5]),
    cirq.rz(np.pi * -0.9153964903)(q[0]),
    cirq.rz(np.pi * -0.9153964903)(q[1]),
    cirq.rz(np.pi * -0.9153964903)(q[2]),
    cirq.rz(np.pi * -0.9153964903)(q[5]),
    u3(np.pi * 0.5, 0, 0)(q[0]),
    u3(np.pi * 0.5, np.pi * 1, 0)(q[1]),
    u3(np.pi * 0.5, np.pi * 1, 0)(q[2]),
    u3(np.pi * 0.5, np.pi * 1, 0)(q[5]),
    cirq.rx(np.pi * 0.5)(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.rx(np.pi * 0.4153964903)(q[0]),
    cirq.ry(np.pi * 0.5)(q[1]),
    cirq.CNOT(q[1], q[0]),
    cirq.rx(np.pi * -0.5)(q[1]),
    cirq.rz(np.pi * 0.5)(q[1]),
    cirq.CNOT(q[0], q[1]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, np.pi * 1)(q[0]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, 0)(q[1]),
    cirq.rz(np.pi * -0.9153964903)(q[0]),
    u3(np.pi * 0.5, 0, 0)(q[0]),
    cirq.rx(np.pi * 0.5)(q[0]),
    cirq.CNOT(q[0], q[2]),
    cirq.rx(np.pi * 0.4153964903)(q[0]),
    cirq.ry(np.pi * 0.5)(q[2]),
    cirq.CNOT(q[2], q[0]),
    cirq.rx(np.pi * -0.5)(q[2]),
    cirq.rz(np.pi * 0.5)(q[2]),
    cirq.CNOT(q[0], q[2]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, np.pi * 1)(q[0]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, 0)(q[2]),
    cirq.rz(np.pi * -0.9153964903)(q[0]),
    u3(np.pi * 0.5, 0, 0)(q[0]),
    cirq.rx(np.pi * 0.5)(q[0]),
    cirq.CNOT(q[0], q[5]),
    cirq.rx(np.pi * 0.4153964903)(q[0]),
    cirq.ry(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[5], q[0]),
    cirq.rx(np.pi * -0.5)(q[5]),
    cirq.rz(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[0], q[5]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, np.pi * 1)(q[0]),
    cirq.rz(np.pi * -0.9153964903)(q[1]),
    cirq.rz(np.pi * -0.9153964903)(q[2]),
    cirq.rz(np.pi * -0.9153964903)(q[3]),
    cirq.rz(np.pi * -0.9153964903)(q[4]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, 0)(q[5]),
    cirq.rx(np.pi * -0.6320733477)(q[0]),
    u3(np.pi * 0.5, 0, 0)(q[1]),
    u3(np.pi * 0.5, np.pi * 1, 0)(q[2]),
    u3(np.pi * 0.5, np.pi * 1, 0)(q[3]),
    u3(np.pi * 0.5, np.pi * 1, 0)(q[4]),
    cirq.rz(np.pi * -0.9153964903)(q[5]),
    cirq.rz(np.pi * 0.1487377097)(q[0]),
    cirq.rx(np.pi * 0.5)(q[1]),
    u3(np.pi * 0.5, np.pi * 1, 0)(q[5]),
    u3(np.pi * 0.5, np.pi * 1.8013661765, np.pi * 1.8013661765)(q[0]),
    cirq.CNOT(q[1], q[2]),
    cirq.rx(np.pi * 0.5)(q[0]),
    cirq.rx(np.pi * 0.4153964903)(q[1]),
    cirq.ry(np.pi * 0.5)(q[2]),
    cirq.CNOT(q[2], q[1]),
    cirq.rx(np.pi * -0.5)(q[2]),
    cirq.rz(np.pi * 0.5)(q[2]),
    cirq.CNOT(q[1], q[2]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, np.pi * 1)(q[1]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, 0)(q[2]),
    cirq.rz(np.pi * -0.9153964903)(q[1]),
    u3(np.pi * 0.5, 0, 0)(q[1]),
    cirq.rx(np.pi * 0.5)(q[1]),
    cirq.CNOT(q[1], q[3]),
    cirq.rx(np.pi * 0.4153964903)(q[1]),
    cirq.ry(np.pi * 0.5)(q[3]),
    cirq.CNOT(q[3], q[1]),
    cirq.rx(np.pi * -0.5)(q[3]),
    cirq.rz(np.pi * 0.5)(q[3]),
    cirq.CNOT(q[1], q[3]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, np.pi * 1)(q[1]),
    cirq.rz(np.pi * -0.9153964903)(q[2]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, 0)(q[3]),
    cirq.rx(np.pi * -0.6320733477)(q[1]),
    u3(np.pi * 0.5, 0, 0)(q[2]),
    cirq.rz(np.pi * 0.1487377097)(q[1]),
    cirq.rx(np.pi * 0.5)(q[2]),
    u3(np.pi * 0.5, np.pi * 1, np.pi * 1.8013661765)(q[1]),
    cirq.CNOT(q[2], q[4]),
    cirq.CNOT(q[0], q[1]),
    cirq.rx(np.pi * 0.4153964903)(q[2]),
    cirq.ry(np.pi * 0.5)(q[4]),
    cirq.rx(np.pi * 0.3512622903)(q[0]),
    cirq.ry(np.pi * 0.5)(q[1]),
    cirq.CNOT(q[4], q[2]),
    cirq.CNOT(q[1], q[0]),
    cirq.rx(np.pi * -0.5)(q[4]),
    cirq.rx(np.pi * -0.5)(q[1]),
    cirq.rz(np.pi * 0.5)(q[4]),
    cirq.rz(np.pi * 0.5)(q[1]),
    cirq.CNOT(q[2], q[4]),
    cirq.CNOT(q[0], q[1]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, np.pi * 1)(q[2]),
    cirq.rz(np.pi * -0.9153964903)(q[3]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, 0)(q[4]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, np.pi * 1)(q[0]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, 0)(q[1]),
    cirq.rx(np.pi * -0.6320733477)(q[2]),
    u3(np.pi * 0.5, np.pi * 1, 0)(q[3]),
    cirq.rz(np.pi * -0.9153964903)(q[4]),
    cirq.rz(np.pi * 0.1487377097)(q[0]),
    cirq.rz(np.pi * 0.1487377097)(q[2]),
    u3(np.pi * 0.5, 0, 0)(q[4]),
    u3(np.pi * 0.5, np.pi * 1.8013661765, np.pi * 1.8013661765)(q[0]),
    u3(np.pi * 0.5, np.pi * 1, np.pi * 1.8013661765)(q[2]),
    cirq.rx(np.pi * 0.5)(q[4]),
    cirq.rx(np.pi * 0.5)(q[0]),
    cirq.CNOT(q[4], q[3]),
    cirq.CNOT(q[0], q[2]),
    cirq.ry(np.pi * 0.5)(q[3]),
    cirq.rx(np.pi * 0.4153964903)(q[4]),
    cirq.rx(np.pi * 0.3512622903)(q[0]),
    cirq.ry(np.pi * 0.5)(q[2]),
    cirq.CNOT(q[3], q[4]),
    cirq.CNOT(q[2], q[0]),
    cirq.rx(np.pi * -0.5)(q[3]),
    cirq.rx(np.pi * -0.5)(q[2]),
    cirq.rz(np.pi * 0.5)(q[3]),
    cirq.rz(np.pi * 0.5)(q[2]),
    cirq.CNOT(q[4], q[3]),
    cirq.CNOT(q[0], q[2]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, 0)(q[3]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, np.pi * 1)(q[4]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, np.pi * 1)(q[0]),
    cirq.rz(np.pi * 0.1487377097)(q[1]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, 0)(q[2]),
    cirq.rz(np.pi * -0.9153964903)(q[3]),
    cirq.rz(np.pi * -0.9153964903)(q[4]),
    cirq.rz(np.pi * 0.1487377097)(q[0]),
    u3(np.pi * 0.5, np.pi * 1.8013661765, np.pi * 1.8013661765)(q[1]),
    cirq.rz(np.pi * 0.1487377097)(q[2]),
    u3(np.pi * 0.5, 0, 0)(q[3]),
    u3(np.pi * 0.5, 0, 0)(q[4]),
    u3(np.pi * 0.5, np.pi * 1.8013661765, np.pi * 1.8013661765)(q[0]),
    cirq.rx(np.pi * 0.5)(q[1]),
    u3(np.pi * 0.5, np.pi * 1, np.pi * 1.8013661765)(q[2]),
    cirq.rx(np.pi * 0.5)(q[3]),
    cirq.rx(np.pi * 0.5)(q[4]),
    cirq.rx(np.pi * 0.5)(q[0]),
    cirq.CNOT(q[1], q[2]),
    cirq.CNOT(q[4], q[5]),
    cirq.rx(np.pi * 0.3512622903)(q[1]),
    cirq.ry(np.pi * 0.5)(q[2]),
    cirq.rx(np.pi * 0.4153964903)(q[4]),
    cirq.ry(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[2], q[1]),
    cirq.CNOT(q[5], q[4]),
    cirq.rx(np.pi * -0.5)(q[2]),
    cirq.rx(np.pi * -0.5)(q[5]),
    cirq.rz(np.pi * 0.5)(q[2]),
    cirq.rz(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[1], q[2]),
    cirq.CNOT(q[4], q[5]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, np.pi * 1)(q[1]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, 0)(q[2]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, np.pi * 1)(q[4]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, 0)(q[5]),
    cirq.rz(np.pi * -0.9153964903)(q[5]),
    u3(np.pi * 0.5, np.pi * 1, 0)(q[5]),
    cirq.CNOT(q[3], q[5]),
    cirq.rx(np.pi * 0.4153964903)(q[3]),
    cirq.ry(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[5], q[3]),
    cirq.rx(np.pi * -0.5)(q[5]),
    cirq.rz(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[3], q[5]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, np.pi * 1)(q[3]),
    cirq.rx(np.pi * -0.6320733477)(q[4]),
    u3(np.pi * 0.5, np.pi * 0.9153964903, 0)(q[5]),
    cirq.rx(np.pi * -0.6320733477)(q[3]),
    cirq.rx(np.pi * -0.6320733477)(q[5]),
    cirq.rz(np.pi * 0.1487377097)(q[5]),
    u3(np.pi * 0.5, np.pi * 1, np.pi * 1.8013661765)(q[5]),
    cirq.CNOT(q[0], q[5]),
    cirq.rx(np.pi * 0.3512622903)(q[0]),
    cirq.ry(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[5], q[0]),
    cirq.rx(np.pi * -0.5)(q[5]),
    cirq.rz(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[0], q[5]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, np.pi * 1)(q[0]),
    cirq.rz(np.pi * 0.1487377097)(q[1]),
    cirq.rz(np.pi * 0.1487377097)(q[3]),
    cirq.rz(np.pi * 0.1487377097)(q[4]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, 0)(q[5]),
    cirq.rx(np.pi * -0.6710086873)(q[0]),
    u3(np.pi * 0.5, np.pi * 1.8013661765, np.pi * 1.8013661765)(q[1]),
    u3(np.pi * 0.5, np.pi * 1, np.pi * 1.8013661765)(q[3]),
    u3(np.pi * 0.5, np.pi * 1, np.pi * 1.8013661765)(q[4]),
    cirq.rz(np.pi * 0.1487377097)(q[5]),
    cirq.rx(np.pi * 0.5)(q[1]),
    u3(np.pi * 0.5, np.pi * 1, np.pi * 1.8013661765)(q[5]),
    cirq.CNOT(q[1], q[3]),
    cirq.rx(np.pi * 0.3512622903)(q[1]),
    cirq.ry(np.pi * 0.5)(q[3]),
    cirq.CNOT(q[3], q[1]),
    cirq.rx(np.pi * -0.5)(q[3]),
    cirq.rz(np.pi * 0.5)(q[3]),
    cirq.CNOT(q[1], q[3]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, np.pi * 1)(q[1]),
    cirq.rz(np.pi * 0.1487377097)(q[2]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, 0)(q[3]),
    cirq.rx(np.pi * -0.6710086873)(q[1]),
    u3(np.pi * 0.5, np.pi * 1.8013661765, np.pi * 1.8013661765)(q[2]),
    cirq.rx(np.pi * 0.5)(q[2]),
    cirq.CNOT(q[2], q[4]),
    cirq.rx(np.pi * 0.3512622903)(q[2]),
    cirq.ry(np.pi * 0.5)(q[4]),
    cirq.CNOT(q[4], q[2]),
    cirq.rx(np.pi * -0.5)(q[4]),
    cirq.rz(np.pi * 0.5)(q[4]),
    cirq.CNOT(q[2], q[4]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, np.pi * 1)(q[2]),
    cirq.rz(np.pi * 0.1487377097)(q[3]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, 0)(q[4]),
    cirq.rx(np.pi * -0.6710086873)(q[2]),
    u3(np.pi * 0.5, np.pi * 1, np.pi * 1.8013661765)(q[3]),
    cirq.rz(np.pi * 0.1487377097)(q[4]),
    u3(np.pi * 0.5, np.pi * 1.8013661765, np.pi * 1.8013661765)(q[4]),
    cirq.rx(np.pi * 0.5)(q[4]),
    cirq.CNOT(q[4], q[3]),
    cirq.ry(np.pi * 0.5)(q[3]),
    cirq.rx(np.pi * 0.3512622903)(q[4]),
    cirq.CNOT(q[3], q[4]),
    cirq.rx(np.pi * -0.5)(q[3]),
    cirq.rz(np.pi * 0.5)(q[3]),
    cirq.CNOT(q[4], q[3]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, 0)(q[3]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, np.pi * 1)(q[4]),
    cirq.rz(np.pi * 0.1487377097)(q[3]),
    cirq.rz(np.pi * 0.1487377097)(q[4]),
    u3(np.pi * 0.5, np.pi * 1.8013661765, np.pi * 1.8013661765)(q[3]),
    u3(np.pi * 0.5, np.pi * 1.8013661765, np.pi * 1.8013661765)(q[4]),
    cirq.rx(np.pi * 0.5)(q[3]),
    cirq.rx(np.pi * 0.5)(q[4]),
    cirq.CNOT(q[4], q[5]),
    cirq.rx(np.pi * 0.3512622903)(q[4]),
    cirq.ry(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[5], q[4]),
    cirq.rx(np.pi * -0.5)(q[5]),
    cirq.rz(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[4], q[5]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, np.pi * 1)(q[4]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, 0)(q[5]),
    cirq.rz(np.pi * 0.1487377097)(q[5]),
    u3(np.pi * 0.5, np.pi * 1, np.pi * 1.8013661765)(q[5]),
    cirq.CNOT(q[3], q[5]),
    cirq.rx(np.pi * 0.3512622903)(q[3]),
    cirq.ry(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[5], q[3]),
    cirq.rx(np.pi * -0.5)(q[5]),
    cirq.rz(np.pi * 0.5)(q[5]),
    cirq.CNOT(q[3], q[5]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, np.pi * 1)(q[3]),
    cirq.rx(np.pi * -0.6710086873)(q[4]),
    u3(np.pi * 0.5, np.pi * 1.0498961138, 0)(q[5]),
    cirq.rx(np.pi * -0.6710086873)(q[3]),
    cirq.rx(np.pi * -0.6710086873)(q[5]),
    cirq.measure(q[0], key='mm0'),
    cirq.measure(q[1], key='mm1'),
    cirq.measure(q[2], key='mm2'),
    cirq.measure(q[3], key='mm3'),
    cirq.measure(q[4], key='mm4'),
    cirq.measure(q[5], key='mm5')
)

simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=8192)
result_dict = dict(result.multi_measurement_histogram(keys=['mm0', 'mm1', 'mm2', 'mm3', 'mm4', 'mm5']))
keys = list(map(lambda arr: reduce(lambda x, y: str(x) + str(y), arr[::-1]), result_dict.keys()))
counts = dict(zip(keys,[value for value in result_dict.values()]))
print(counts)
with open('cirq.circuit', 'w') as f:
    print(circuit.to_text_diagram(), file=f)
