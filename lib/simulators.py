from abc import ABC
from abc import abstractmethod

from qiskit import QuantumCircuit
from qiskit import QuantumCircuit, Aer, execute

import cirq
from cirq import Simulator
from cirq.contrib.qasm_import import circuit_from_qasm
from cirq.ops.measurement_gate import MeasurementGate


# CIRQ: supporting function
def get_all_measurement_keys(circuit):
    all_ops = list(circuit.findall_operations_with_gate_type(MeasurementGate))
    return sorted([e[2].key for e in all_ops])


class Circuit(ABC):

    def __init__(self, repetitions=1024):
        self.result = None
        self.circuit = None
        self.repetitions = repetitions

    @abstractmethod
    def from_qasm(self, qasm_string):
        pass

    @abstractmethod
    def execute(self, classical_input=None):
        pass

    @abstractmethod
    def draw(self):
        pass

    def get_result(self):
        return self.result


class QiskitCircuit(Circuit):

    def __init__(self, repetitions=1024):
        super(QiskitCircuit, self).__init__(repetitions)
        self.platform_name = 'qiskit'
        # aer_simulator | qasm_simulator
        self.simulator = Aer.get_backend("aer_simulator")

    def from_qasm(self, qasm_string):
        self.circuit = QuantumCircuit.from_qasm_str(qasm_string)

    def execute(self, classical_input=None):
        job = execute(self.circuit, self.simulator)
        job_result = job.result()
        self.result = dict(job_result.get_counts())

    def draw(self):
        print(self.circuit.draw())


class CirqCircuit(Circuit):

    def __init__(self, repetitions=1024):
        super(CirqCircuit, self).__init__(repetitions)
        self.platform_name = 'cirq'
        self.simulator = Simulator()

    def from_qasm(self, qasm_string):
        # remember to add the QASM header

        chunks = qasm_string.split("barrier q;")
        preface = "\n".join(qasm_string.split("\n")[:5])
        # preface contains standatd lib and registers
        # print(preface)

        # extract the input preparation part (before the 1st barrier)
        # create it with circuit_from_qasm(chunk_input)
        chunk_input = chunks[0]

        # extract the central part (between barriers)
        # create it with circuit_from_qasm(chunk_core)
        chunk_core = preface + chunks[1]

        # extract the last part (after 2nd barrier)
        # create it with circuit_from_qasm(chunk_measurement)
        chunk_measurement = preface + chunks[2]

        # glue the three chunks making sure they are executed in different
        # moments
        # hint: use append

        self.circuit = circuit_from_qasm(chunk_input) + circuit_from_qasm(chunk_core) + circuit_from_qasm(chunk_measurement)  # noqa

    def execute(self, classical_input=None):
        samples = self.simulator.run(
            self.circuit, repetitions=self.repetitions)
        all_keys = get_all_measurement_keys(self.circuit)
        counter = samples.multi_measurement_histogram(keys=all_keys)
        self.result = {
            "".join([str(d) for d in e][::-1]): int(v)
            for (e, v) in counter.items()
        }

    def draw(self):
        print(self.circuit.to_text_diagram())
