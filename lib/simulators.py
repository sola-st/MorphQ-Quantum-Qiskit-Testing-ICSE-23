from abc import ABC
from abc import abstractmethod

from qiskit import QuantumCircuit
from qiskit import QuantumCircuit, Aer, execute

import cirq
from cirq import ops
from cirq import Simulator
from cirq.contrib.qasm_import import circuit_from_qasm
from cirq.ops.measurement_gate import MeasurementGate

from pathlib import Path
import re
import os
import hashlib
import yaml




from utils import convert_single_program
from utils import run_single_program


# CIRQ: supporting function
def get_all_measurement_keys(circuit):
    all_ops = list(circuit.findall_operations_with_gate_type(MeasurementGate))
    return sorted([e[2].key for e in all_ops])


def extract_registers_and_body(qasm_string):
        """Extracts register definitions and body from the QASM string.
        """
        lines = qasm_string.split("\n")
        register_lines = []
        body = []
        for line in lines:
            if line.startswith("creg"):
                register_lines.append(line)
            elif line.startswith("qreg"):
                register_lines.append(line)
            elif line.startswith("OPENQASM") or line.startswith("include"):
                pass
            else:
                body.append(line)
        return register_lines, body


class Circuit(ABC):

    def __init__(self, repetitions=1024):
        self.result = None
        self.circuit = None
        self.repetitions = repetitions

    @abstractmethod
    def from_qasm(self, qasm_string):
        pass

    @abstractmethod
    def to_custom_string(self):
        pass

    @abstractmethod
    def execute(self, custom_shots=None):
        pass

    @abstractmethod
    def draw(self, file=None):
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

    def to_custom_string(self):
        return self.circuit.qasm()

    def execute(self, custom_shots=None):
        shots = custom_shots
        if shots is None:
            shots = self.repetitions
        job = execute(self.circuit, self.simulator, shots=shots)
        job_result = job.result()
        self.result = dict(job_result.get_counts())

    def draw(self, file=None):
        if file is not None:
            print(self.circuit.draw(), file=file)
        print(self.circuit.draw())


class CirqCircuit(Circuit):

    def __init__(self, repetitions=1024):
        super(CirqCircuit, self).__init__(repetitions)
        self.platform_name = 'cirq'
        self.simulator = Simulator()

    def from_qasm(self, qasm_string):
        # check if barriers are present
        if any([
                line.startswith("barrier")
                for line in qasm_string.split("\n")]):

            preface = "OPENQASM 2.0;" + "\n" + 'include "qelib1.inc";' + "\n"

            register_lines, body = \
                extract_registers_and_body(qasm_string)
            preface = preface + "\n".join(register_lines) + "\n"
            qasm_string = "\n".join(body)

            # split in different barriers (operation not supported by cirq)
            chunks = re.split("barrier.*;", qasm_string)
            first_chunk = chunks[0]
            self.circuit = circuit_from_qasm(preface + first_chunk)
            other_chunks = chunks[1:]
            for chunk in other_chunks:
                self.circuit += circuit_from_qasm(preface + chunk)
        else:
            self.circuit = circuit_from_qasm(qasm_string)

        # rename all the measurements
        self.circuit = self._give_unique_ids_to_measurement()

    def to_custom_string(self):
        return cirq.to_json(self.circuit)

    def execute(self, custom_shots=None):
        shots = custom_shots
        if shots is None:
            shots = self.repetitions
        samples = self.simulator.run(
            self.circuit, repetitions=shots)
        all_keys = get_all_measurement_keys(self.circuit)
        counter = samples.multi_measurement_histogram(keys=all_keys)
        self.result = {
            "".join([str(d) for d in e][::-1]): int(v)
            for (e, v) in counter.items()
        }

    def draw(self, file=None):
        if file is not None:
            print(self.circuit.to_text_diagram(), file=file)
        print(self.circuit.to_text_diagram())

    def _give_unique_ids_to_measurement(self):
        """Give unique ids to the measurements in the circuit."""
        new_circuit = []
        unique_id = 0
        for m in self.circuit:
            #print(m)
            new_moment_ops = []
            for op in m.operations:
                if isinstance(op.gate, ops.MeasurementGate):
                    new_measurement = cirq.measure(
                        op.qubits[0], key=f"m_{unique_id}")
                    unique_id += 1
                    new_moment_ops.append(new_measurement)
                else:
                    new_moment_ops.append(op)
            #print(new_moment_ops)
            new_circuit.append(cirq.Moment(new_moment_ops))
        return cirq.Circuit(new_circuit)


class QconvertCircuit(Circuit):

    def __init__(self, target_platform="qiskit", repetitions=1024):
        super(QconvertCircuit, self).__init__(repetitions=repetitions)
        # load yaml file
        with open("../config/qconvert_settings.yaml", 'r') as yaml_file:
            config = yaml.load(yaml_file, Loader=yaml.FullLoader)
        self.qconvert_path = config["qconvert_path"]
        self.python_path = config["python_path"]
        self.platforms = config["platforms"]
        self.platform_name = f'qconvert_{target_platform}'
        self.target_platform = target_platform
        # create a local cache folder
        self.tmp_folder = "./qconvert_tmp_cache"
        Path(self.tmp_folder).mkdir(parents=True, exist_ok=True)

    def from_qasm(self, qasm_string):
        self.qasm_string = qasm_string
        # materialize a tmp qasm file
        to_encode = qasm_string + self.target_platform
        self.qasm_digest = hashlib.sha224(to_encode.encode('utf-8')).hexdigest()
        self.qasm_path = os.path.join(self.tmp_folder, self.qasm_digest + ".qasm")
        with open(self.qasm_path, "w") as qasm_file:
            qasm_file.write(qasm_string)
        self.platform_path = convert_single_program(
            target_program=self.qasm_path,
            dest_folder=self.tmp_folder,
            dest_format=self.target_platform,
            qconvert_path=self.qconvert_path)
        # read the file at the platform_path
        with open(self.platform_path, "r") as platform_file:
            self.platform_string = platform_file.read()

    def to_custom_string(self):
        custom_string = "QASM:\n"
        custom_string += "-" * 80 + "\n"
        custom_string += self.qasm_string + "\n"
        custom_string += "-" * 80 + "\n"
        custom_string += self.target_platform + "\n"
        custom_string += "-" * 80 + "\n"
        custom_string += self.platform_string + "\n"
        self.custom_string = custom_string
        return custom_string

    def execute(self, custom_shots=None):
        shots = custom_shots
        if shots is None:
            shots = self.repetitions
        # rewrite the number of shots
        with open(self.platform_path, "w") as platform_file:
            my_platform = self.platforms[self.target_platform]
            platform_file.write(self.platform_string.replace(
                my_platform["shots_lookup"],
                my_platform["shots_substitute"].format(injected_shot=shots)))
        # execute the file
        self.result = run_single_program(
            target_file=self.platform_path,
            dest_folder=self.tmp_folder,
            python_path=self.python_path)

    def draw(self, file=None):
        print(self.to_custom_string())