from hashlib import new
import os
import random
import json
from collections import Counter
from multiprocessing import Pool

import pandas as pd
import numpy as np

N_QUBITS = 10
N_EVALUATIONS = 100
N_SHOTS = 1024
N_RANDOM_DIGITS = 10
OUT_FOLDER = "../data/random_bitstrings"
N_THREADS = 10


def random_qc_result(n_qubits, n_shots):
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


def generate_random_bitstring(out_folder):
    print("Creating random dataset")

    # perform 30 evaluations [N_EVALUATION]
    data = []
    for i in range(N_EVALUATIONS):
        # run the circuit for 1024 or 8096 shots
        data.append(random_qc_result(N_QUBITS, N_SHOTS))

    # save the statistics for each combination to a dataframe
    df = pd.DataFrame.from_records(data)

    random_id = str(
        random.randint(0, 10**N_RANDOM_DIGITS)).zfill(N_RANDOM_DIGITS)

    df.to_csv(
        os.path.join(out_folder, f"{random_id}_random.csv"))

    metadata_dict = {
        "random_id": random_id,
        "n_qubits": N_QUBITS,
        "n_evaluations": N_EVALUATIONS,

    }

    with open(os.path.join(out_folder, f"{random_id}.json"), "w") as f:
        json.dump(metadata_dict, f)


def main():
    """Simulate circuits."""
    with Pool(N_THREADS) as p:
        p.map(generate_random_bitstring, [OUT_FOLDER] * 1000)


if __name__ == "__main__":
    main()
    print("Done")
