
import click
import yaml

import numpy as np
import math
from math import sqrt

import json
import random
import os
import time

from simulators import *

from typing import Dict, Any


def qdiff_formula(n_qubits: int, platform_constant: float):
    """Calculate the sample size as in the QDiff paper."""
    t = 0.1
    p = 2/3
    A = platform_constant
    return A * (1 / sqrt(1 - p)) * sqrt(m) * t**(-2)


def get_qasm_files(path: str):
    """Get all the qasm files in the directory."""
    return [
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.endswith(".qasm")
    ]


@click.command()
@click.argument('config_file')
def main(config_file):
    """Execute programs according to the CONFIG_FILE."""
    # check that there is a file at the config file location
    assert os.path.isfile(config_file), "Config file does not exist."
    # load the config file with yaml
    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    # check that the config file has the right keys
    keys = config.keys()
    required_keys = [
        "platforms_objects",
        "strategy_sample_size_estimation",
        "fixed_sample_size",
        "n_repetitions",
        "strategy_input_generation",
        "fixed_input",
        "folder_generated_qasm", "folder_execution_results"]
    for req_key in required_keys:
        assert req_key in keys, f"Config file missing key: {req_key}"

    # get the qasm files
    qasm_files = get_qasm_files(config["folder_generated_qasm"])
    for simulator_object_name in config["platforms_objects"]:
        # instantiate an object named simulator_object_name
        simulator_object = eval(
            simulator_object_name)(repetitions=config["fixed_sample_size"])
        for qasm_file in qasm_files:
            # read the file content
            with open(os.path.join(config["folder_generated_qasm"], qasm_file), "r") as f:
                qasm_content = f.read()
            # load the quantum program
            simulator_object.from_qasm(qasm_content)
            # determine the number of shots, which are significant for the
            # comparison later
            if config["strategy_sample_size_estimation"] is not None:
                metadata_filename = os.path.splitext(qasm_file)[0] + ".json"
                with open(os.path.join(
                        config["folder_generated_qasm"],
                        metadata_filename), "r") as f:
                    metadata_dict = json.load(f)
                n_qubits = metadata_dict["n_qubits"]
            # execute the quantum program
            if config["strategy_sample_size_estimation"] == 'qdiff':
                shots = qdiff_formula(n_qubits, 12)
                simulator_object.execute(shots)
            else:
                simulator_object.execute()
            # save the execution results
            file_name = "{}_{}".format(
                os.path.splitext(qasm_file)[0], simulator_object_name)
            print(file_name)
            result = simulator_object.get_result()
            with open(os.path.join(config["folder_execution_results"],
                                   f"{file_name}.json"), "w") as f:
                json.dump(result, f)


if __name__ == '__main__':
    main()