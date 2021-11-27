# load json file
library(jsonlite)
# load csv library
library(data.table)
library(energy)


# load data
#data <- fromJSON("../data/MVP/execution_results/1637950927_1010_CirqCircuit.json")


# read csv
A <- read.csv("../data/MVP/A.csv", header=TRUE)
B <- read.csv("../data/MVP/B.csv", header=TRUE)
# measure the length of the data
n <- nrow(A)
m <- nrow(B)

X <- rbind(A, B)
d <- dist(X)

# should match edist default statistic
set.seed(1234)
eqdist.etest(d, sizes=c(n, m), distance=TRUE, R = 30)

# print first 5 rows
head(A)