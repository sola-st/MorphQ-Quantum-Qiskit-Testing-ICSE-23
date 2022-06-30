# qubit number=3
# total number=2

import numpy as np

from qiskit import QuantumCircuit, execute, Aer, QuantumRegister, ClassicalRegister, transpile, BasicAer, IBMQ
import networkx as nx
from qiskit.visualization import plot_histogram
from typing import *
from pprint import pprint
from math import log2
from collections import Counter
from qiskit.test.mock import FakeVigo, FakeYorktown

kernel = 'circuit/bernstein'


def make_circuit(n:int) -> QuantumCircuit:
    # circuit begin
    input_qubit = QuantumRegister(n,"qc")
    prog = QuantumCircuit(input_qubit)

    for edge in E:
        k = edge[0]
        l = edge[1]
        prog.cp(-2 * gamma, input_qubit[k-1], input_qubit[l-1])
        prog.p(gamma, k)
        prog.p(gamma, l)

    prog.rx(2 * beta, range(len(V)))

    # circuit end

    return prog



if __name__ == '__main__':
    n = 4
    V = np.arange(0, n, 1)
    E = [(0, 1, 1.0), (0, 2, 1.0), (1, 2, 1.0), (3, 2, 1.0), (3, 1, 1.0)]

    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_weighted_edges_from(E)

    step_size = 0.1

    a_gamma = np.arange(0, np.pi, step_size)
    a_beta = np.arange(0, np.pi, step_size)
    a_gamma, a_beta = np.meshgrid(a_gamma, a_beta)

    F1 = 3 - (np.sin(2 * a_beta) ** 2 * np.sin(2 * a_gamma) ** 2 - 0.5 * np.sin(4 * a_beta) * np.sin(4 * a_gamma)) * (
                1 + np.cos(4 * a_gamma) ** 2)

    result = np.where(F1 == np.amax(F1))
    a = list(zip(result[0], result[1]))[0]

    gamma = a[0] * step_size
    beta = a[1] * step_size

    prog = make_circuit(4)
    sample_shot =5600
    writefile = open("../data/startQiskit_Class0.csv", "w")
    # prog.draw('mpl', filename=(kernel + '.png'))
    backend = BasicAer.get_backend('statevector_simulator')

    circuit1 = transpile(prog, FakeYorktown())
    prog = circuit1

    info = execute(prog,backend=backend, shots=sample_shot).result().get_counts()

    print(info, file=writefile)
    print("results end", file=writefile)
    print(circuit1.depth(), file=writefile)
    print(circuit1, file=writefile)
    writefile.close()
