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

# Generation of Algorithms for Testing
If an algorithm has an output probability which is almost completely uniform, it is unusable also by a fully functional quantum computer, because to get the most probable result, namely the solution to our problem of interest, we need to run our program for a very large number of shots.
> **Peaked Output**: the output probability should be very peaked on few bitstrings to have high chance to recognize the correct solution to our problem.

At the same time, the classical programs are a subset of a quantum programs, because the quantum gate can simulate the logic ports used in every classical circuit (e.g. NAND gate).
Thus if a circuit is peaked because it is exactly one of those classical programs, we are less interested in it.
> **Spread Intermediate State**: we want the intermediate state (half of the execution) of a quantum programs contains some superposition of bitstrings, i.e., a very spread distribution, almost uniform.


# Ideas

1. use some ansazt from Quantum ML and learn the parameters of the circuit to maximize the high uniformity and spread in the distribution of the intermediate state (half distribution), and maximize the peakness of the final output distribution.