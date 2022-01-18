from abc import ABC
from abc import abstractmethod

import random
from collections import Counter

from simulators import Circuit


class UniformBitstringDistribution(Circuit):

    def from_qasm(self, qasm_string):
        self.n_qubits = int(qasm_string.split("#")[0])

    def execute(self, custom_shots=None):
        shots = custom_shots
        if shots is None:
            shots = self.repetitions
        self.result = self.random_qc_result(n_qubits=self.n_qubits, n_shots=shots)
        return self.result

    def draw(self):
        print(f"No real qasm. Execution results simulated with: {self.__class__.__name__}.")

    def to_custom_string(self):
        return f"{self.__class__.__name__}({self.n_qubits})"

    def random_qc_result(self, n_qubits, n_shots):
        """Create a random quantum circuit result."""

        max_int = 2**n_qubits - 1

        results = []
        for _ in range(n_shots):
            sample = random.randint(0, max_int)
            format_string = "{0:" + str(n_qubits) + "b}"
            string_result = format_string.format(sample).zfill(n_qubits)
            results.append(string_result)

        res_dict = {
            k.replace(" ", "0"): v
            for k, v in Counter(results).items()
        }
        return res_dict
