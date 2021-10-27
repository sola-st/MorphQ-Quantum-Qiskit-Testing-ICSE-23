# Neural Execution

1. What do we want to emulate with a neural network?
    - an arbitrary gate circuit?
    - a specialized circuit for one application (e.g., grover algorithm, quantum fourier transform, etc...)
    "Neural-network states for the classical simulation of quantum computing" Giuseppe Carleo, 2018, simulated "Hadamard and Fourier transform of entangled initial states with Restricted Boltzmann Machines"
1. If we focus on an entire circuit, which depth should we use?
1. How many qubits do we consider?
    - are 10 enough?
1. How do we construct the pairs input-output?
    - (ideal) simulator runs
    - (noisy model) simulator runs
    - real quantum computer run (warning: unavoidable noise)
1. Which part of the program are we emulating with a NN?
    - end-to-end: given an input program U and a concrete input quantum state |x>, we give the distribution of the quantum state |y>, obtained by |y> = U * |x>
    - step by step: given a single gate G and the qubit(s) it acts on, plus the input state |x_0>, we give the state |X_1> as output of the