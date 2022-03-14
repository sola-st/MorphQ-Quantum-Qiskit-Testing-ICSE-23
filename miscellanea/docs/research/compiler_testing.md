# Compiler Testing


Decisions:
1. which part of the quantum computing workflow we want to test?
	- program parsing? (from Qasm low level language or Quil from Rigetti)
	- optimization passes?
	- noise simulation?
1. Do we want to study a setting which is in common to many application (e.g., program parsing), or only to some specific application (e.g., QUBO formulation for optimization problems)
1. How to generate the program?
	- randomly (is it realistic?)
	- focus only on those circuit which give a "realistic" quantum algorithm output, aks with few results that have the highest output probability.
1. which gates to use?

## Detector Ideas

1. how to evaluate if the output is the same between two compilers? (remember that we are comparing distributions of bitstrings [0111010101: freq, etc...])
	- statistical test on the mean of each bitstring
	- statistical test on the mean of the top-K bitstring
	- statistical test on each bit separately
	- Kolmogorov-Smirnov (KS) test: The two-sample K–S test is one of the most useful and general nonparametric methods for comparing two samples, as it is sensitive to differences in both location and shape of the empirical cumulative distribution functions of the two samples.
	- QDiff approach to compare simulations: "closeness testing in L1 norm [17] to estimate the required number of measurements given confidence level p = 2/3. [...] To compare two sets of measurements, QDiff uses distribution comparison methods: K-S and Cross Entropy are now supported."
	- map the output to a two dimensional output (e.g. with t-sne, PCA) and use a 2D statistical test to compare.
	- anomaly detection based (e.g., isolation forest based), to check if the points of the Distribution A are detected as outliers when compared to the points of the Distribution B (on which the model was trained on).
	- check the statistics of a single qubit, check the statistics of pairs of qubits happening together, etc.. inspired by monograms, diagrams, etc.. in BLEU score.
	- naive bayes: check if a trained naive bayes model, which is based on the single qubit occurrences, can learn to predict whether the datapoint comes from platform A or B. Note that Naive Bayes, has as assumption that the variable (in this case the qubit) are independent, whereas in our cas, due to the entanglement, they are not independent.
	- run them in **state vector mode** and compare the state vectors (length: 2^n and numerical instability are possible).
	- right before execution, thus after the optimizations made by the platform,extract the QASM code and compare that between platforms. problem: one optimization might have removed two opposite operations which had no net effect.
	- ranking based: get the most popular 100 bitstrings for platform A, the most popular for platform B. Use the spearman rank coefficient to see how much they agree. If possible use a weighted version, so that the values at the beginning of the rank value more.

## Benchmark of Detectors

1. How do we sanity-check our method/test (MAGIC-TEST) for distribution comparison? Positive (rejects null hp): the test detects a difference between the two distributions. Negative: the test says that the two distributions are indistinguishable.
	- focus on one platform only; check if it is able to distinguish between the distribution of outputs of the real simulation and randomly generated bitstrings. (easy TRUE POSITIVE WORKs)
	- no platform needed; randomly generated bitstrings to simulate two platforms A and B, using the same distribution. The method should not raise any alarm/positive, because the distributions are identical by construction. (easy TRUE NEGATIVE WORKs)
	- focus on one platform only; generate 2096 outputs from a single quantum program for the same platform. The method should not raise any alarm/positive, because the distributions are identical by construction, since produced by the same platform. (realistic TRUE NEGATIVE WORKs)
	- focus on a pool of famous algorithms, already present in the official repos of both libraries; run them on both A and B platforms; collect the outputs. Assumption: those implementations are corrected and have been independently tested. Check if our magic-test do not raise false positive among those, which are supposedly correctly implemented. (real TRUE NEGATIVE cross-platform) (low FALSE POSITIVE on gold standard programs).
	- focus on one platform only; execute the Qasm program to get distribution A, then append one or more CNOT to the end (before the measurement) and execute it to get distribution B. Assumption: the CNOT highly impacted the program, thus the output should be different. We expect the model to raise an alarm for all of the pairs. (realistic TRUE POSITIVE WORKs).
	- run program A on platform A, then run program A followed by all X gate on the same platform. The X gates should have generated a specular distribution, which means that the detector should raise an alarm, unless the distribution was symmetric since the beginning.
	- focus on one platform, running program A and Program B, they should be distinguished as two different distributions by our method.
	- develop a method which is provable correct and returns "these distributions are the same" only when there are actually the same. No false positive.
	- develop a method which is provable correct and returns "these distributions are different" only when there are actually different. No false negative.
	- run Program 1 in Framework A, the method should distinguish the distribution of P1 and the output of P1 where we reverse all the qubits.



## Input Reduction > Minimal Bug

1. How to find the  bug triggering quantum program?
	- incremental strategy: start by running the qasm on both platforms, only the first instruction, then if they given identical output, add another instruction, until you reach all the instructions.
	- divide ans conquer strategy: split the circuit in two from the middle and see if the one creating problems is the first or second half, repeat this recursively to find the involved operations. Note that more than one chunk might be faulty if the same faulty optimization is applied in multiple points in the program.


## Improve Experiment Efficiency - Dataset
1. how to create a **platform** dataset (to save computation)?
	- create a dataset of encodings for circuits, run them and get its output bitstrings and their outputs for both platforms.
1. How to speed up the dataset creation?
	- sample twice as many samples to avoid rerunning the same circuit twice in the future.
1. how to create a random dataset?
	- Create a dataset of random bitstrings and reuse that instead of resampling it every time.
1. how to store the dataset?
	- simple files: named with a unique hash. Json format to store info on:
		- numeric encoding (direct mapping to a qasm program)
		- for each platform:
			- Platform A: dec_value->frequency (1024 shots) repeated 100 times
			- Platform B: dec_value->frequency (1024 shots) repeated 100 times


