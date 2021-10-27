# Algorithm Design

When a quantum computer runs a program of 20 qubits, then the results lies in a space of 2^20.
If the output has many possible solutions (bitstrings) with high frequencies then to have a clear idea which is the best one we have to sample the output many many times until we realize, for example, that string 10011....10 appears 50k, whereas solution 01101..10 appears 51k, out of a total of maybe a million of sampling.
This shows how it is very difficult for us to observe the output quantum state, thus it is important that the final output is a quantum state where only few bitstirngs are possible (e.g. 1k of bitstrings out of 2^20 can appear in the output), and not all of them.


## Genetic Algorithms

Idea: use genetic algorithm to MAXIMIZE:
- the number of gates acting on each qubit (so we do not have any idle qubit)
- the number of CNOT as proxy for entanglements (otherwise the algorithm is not quantum)

and MINIMIZE
- the number of possible output solutions;
- the consistency over different input bit strings (encoded as plain 0 or 1 qubits, with a not gate in front).

1. Which mutation is relevant for creating new programs out of previous "good" programs?
1. How can we understand what each produced program is doing? Without knowing that the algorithms are useless form a practical point of view.