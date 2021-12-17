# load json
library(jsonlite)
library(yaml)
# import dataframe library
#library(data.table)
library(dplyr)
library(energy)

# get command line argument
args <- commandArgs(trailingOnly = TRUE)

# read yaml file
yaml <- read_yaml(file=args[1])


input_root_folder <- yaml$folder_execution_results
output_root_folder <- yaml$folder_comparison_results

read_file <- function(result_file) {
    # read json file into a dictionary
    print(paste("Loading: ", result_file))
    json_dict <- fromJSON(txt=result_file)
    print("Loading successful.")

    # convert a list to a data frame in tidyverse
    df <- data.frame(cbind(names(json_dict), json_dict), stringsAsFactors=FALSE)
    row.names(df) <- NULL
    # rename column V1 to number
    names(df)[names(df) == 'V1'] <- 'bitstring'
    names(df)[names(df) == 'json_dict'] <- 'ntimes'

    # split columns
    df <- within(df, bitstring<-data.frame(do.call('rbind', strsplit(as.character(bitstring), '', fixed=TRUE))))
    df_unpacked <- as.data.frame(lapply(df$bitstring, unlist))
    # gen number of columns
    ncols <- length(names(df_unpacked))
    df_unpacked$ntimes <- df$ntimes
    df <- df_unpacked
    head(df_unpacked)
    print(colnames(df_unpacked))

    # replicate the rows a number of time expresed by the frequency column
    df <- df[rep(row.names(df), df$ntimes), 1:ncols]

    df <- as.data.frame(df)
    row.names(df) <- NULL
    return(df)
}


filenames <- list.files(input_root_folder)

root_filenames <- sub('[a-zA-Z]+.json','', filenames)
root_filenames <- sub('pvalue.txt','', root_filenames)

# get unique file in root_filenames
unique_filenames <- unique(root_filenames)

print(unique_filenames)
platforms <- c("CirqCircuit.json", "QiskitCircuit.json")

for (file in unique_filenames) {
    platform_A <- paste(file, platforms[1], sep="")
    platform_B <- paste(file, platforms[2], sep="")

    dataset_A <- read_file(paste(input_root_folder, platform_A, sep="/"))
    dataset_B <- read_file(paste(input_root_folder, platform_B, sep="/"))
    n = nrow(dataset_A)
    m = nrow(dataset_B)

    print("Distance Computation")
    X <- rbind(dataset_A, dataset_B)
    d <- dist(X)

    # should match edist default statistic
    set.seed(1234)
    print("Test Computation")
    statistic <- eqdist.etest(d, sizes=c(n, m), distance=TRUE, R = 499)
    #sink(paste(output_root_folder, paste(file, "pvalue.txt", sep=""), sep="/"))
    #print(statistic)
    #sink()
    print(statistic)

    # save json file
    s <- as.double(statistic$statistic)
    p <- as.double(statistic$p.value)
    typeof(statistic$statistic)
    typeof(statistic$p.value)
    serialized_statistic <- list(statistic = s, p_value = p)
    print(serialized_statistic)
    exportJSON <- toJSON(serialized_statistic, auto_unbox = TRUE)
    print(exportJSON)
    write(exportJSON, paste(output_root_folder, paste(file, "energy", ".json", sep=""), sep="/"))

}

#head(dataset_A)
#head(dataset_B)

#X <- rbind(dataset_A, dataset_B)
#dataset_X <- data.frame(X)

#head(dataset_X)
#print(nrow(dataset_X))
