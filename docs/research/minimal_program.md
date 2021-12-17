Once we identify a divergence, we need a strategy to identify the minimal sequence of operations which trigger it to help the understanding and debugging of the program.


## "Dropout" inspired

We create some variants of the program and for each variant we run it again on the two platforms and compare the results.
Each variant is a subset of the original program.
Where we find a difference, we add a negative weight to all the operations and qubits involved in the variant under test.
On the other side, if the variant doesn't trigger the divergence alarm, then we give a positive weight to the qubits and operations involved in it.

Some ideas to create variants could be to:
1. remove some operations with uniform probability, aka completely randomly.
1. split the program depth-wise and execute the first half, then the second half as two variants.
1. split the program bit-wise, divide the bits in two subsets. Create a variant for each subset. Each variant uses only operations which are completely included in the subset. Warning: 2-qubits operations between the two subsets are not part of any variant.


Idea: use a genetic algorithm to minimize the program. The solution is represented as a 0 and 1 binary string for each operation and qubit in the program. The fitness function minimize the length (low number of operations) and maximize the divergence (lower p-value).

