# Hypothesis Testing

An extensive reference for distance between distributions can be found here [1].

[1]: http://www2.math.uu.se/~svante/papers/sjN21.pdf


Some examples of hypothesis testing with their source and reference:


## Uniform vs non uniform

"uniformity testing, i.e., distinguishing between the case that an unknown distribution p (accessible via samples) is uniform versus ε-far from uniform.
Goldreich and Ron *GR00*, motivated by a connection to testing expansion in graphs, obtained a uniformity tester using O( n/ε^4 ) samples.
Subsequently, Paninski gave the  tight bound of Θ( n/ε^2 ) [Pan08]."

Quote from: Optimal Algorithms for Testing Closeness of Discrete Distributions, 2013

*GR00*  O. Goldreich and D. Ron. On testing expansion in bounded-degree graphs. 2000
*Pan08* L. Paninski. A coincidence-based test for uniformity given very sparsely-sampled discrete data., 2008

## Closeness testing in L1



## How to get a p-value for a test?

We can simulate two samples extracted from the same distribution and apply the test.
This will give us the distribution of values of the test statistic under the null hypothesis.
Thus at test time, we get a test statistic of t1, and we can compute the p-value of the test by measuring the area of the distribution of test statistic greater then t1.




