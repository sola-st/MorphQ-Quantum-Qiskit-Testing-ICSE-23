import click
import yaml

import numpy as np
import pandas as pd
import math

import json
import random
import os
import time

from detectors import *

from typing import Dict, Any


def load_json(filename, folder):
    """
    Read the json file at the given path.
    """
    with open(os.path.join(folder, filename), 'r') as f:
        return json.load(f)


def get_execution_files(path, platform_A, platform_B):
    """
    Return a list of the execution files in the given path.
    """
    list_files = os.listdir(path)  # Get all the files in the path
    platform_A_files = set([
        f.replace(f'{platform_A}.json', "") for f in list_files
        if f.endswith(f'{platform_A}.json')
    ])
    platform_B_files = set([
        f.replace(f'{platform_B}.json', "") for f in list_files
        if f.endswith(f'{platform_B}.json')
    ])
    print(platform_A_files)
    print(platform_B_files)
    intersection = list(platform_A_files.intersection(platform_B_files))
    return [
        (
            load_json(e + f'{platform_A}.json', folder=path),
            load_json(e + f'{platform_B}.json', folder=path),
            e[:-1]  # last character is the '_'
        )
        for e in intersection
    ]


@click.command()
@click.argument('config_file')
def main(config_file):
    """Generate programs according to the CONFIG_FILE."""
    # check that there is a file at the config file location
    assert os.path.isfile(config_file), "Config file does not exist."
    # load the config file with yaml
    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    # check that the config file has the right keys
    keys = config.keys()
    required_keys = [
        "strategy_execution_comparison_in_python",
        "platforms_objects",
        "folder_execution_results",
        "folder_comparison_results"
        ]
    for req_key in required_keys:
        assert req_key in keys, f"Config file missing key: {req_key}"

    detectors = []

    if "ks" in config["strategy_execution_comparison_in_python"]:
        detectors.append(KS_Detector())

    # get pairs of dictionary
    platforms = config["platforms_objects"]
    assert len(platforms) == 2, "There should be two platforms."
    platform_A, platform_B = platforms
    # get the execution files
    pairs_of_results = get_execution_files(
        config["folder_execution_results"],
        platform_A, platform_B)

    for (result_A, result_B, identifier) in pairs_of_results:
        # get the results
        for detector in detectors:
            statistic, p_value = detector.check(result_A, result_B)
            comparison = {
                "statistic": statistic,
                "p_value": p_value,
            }
            with open(os.path.join(
                        config["folder_comparison_results"],
                        identifier + ".json"
                    ), "w") as f:
                json.dump(comparison, f)


if __name__ == '__main__':
    main()
