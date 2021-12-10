""""
Benchmark for the detectors of divergent input.


In this file you can:
- create a new benchmark (see the function `create_benchmark`)
- run the benchmark with a new detector (see the function `run_benchmark`)
"""


import click
import yaml

import numpy as np
import pandas as pd
import math

import json
import random
import os
import time
from pathlib import Path

from detectors import *
from generation_strategy import *
from simulators import *
from simulators_mockup import *

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


def check_folder_structure(config):
    """Check that the folder structure is correct."""
    click.echo("Checking folder structure...")
    benchmarks = config["benchmarks_configurations"]
    benchmark_names = [benchmark["name"] for benchmark in benchmarks]
    benchmark_folder = config["folder_benchmark"]
    Path(benchmark_folder).mkdir(parents=True, exist_ok=True)
    for benchmark_name in benchmark_names:
        subfolder = os.path.join(benchmark_folder, benchmark_name)
        Path(subfolder).mkdir(parents=True, exist_ok=True)
        for stage_folder in ["programs", "executions", "ground_truth", "predictions"]:
            Path(os.path.join(subfolder, stage_folder)).mkdir(
                parents=True, exist_ok=True)
            for sample_name in ["sample_a", "sample_b"]:
                Path(os.path.join(subfolder, stage_folder, sample_name)).mkdir(
                    parents=True, exist_ok=True)
    click.echo("Folder structure checked and ready.")


def get_benchmark_folder(config: Dict[str, Any], benchmark_name: str, stage: str, sample: str) -> str:
    """Get the benchmark folder from the config file."""
    assert stage in ["programs", "executions", "ground_truth", "predictions"]
    assert benchmark_name in [b["name"] for b in config["benchmarks_configurations"]]
    assert sample in ["sample_a", "sample_b"]
    return os.path.join(config["folder_benchmark"], benchmark_name, stage, sample)


def joined_generation(benchmark_name: str, benchmark_config: Dict[str, Any], config: Dict[str, Any]):
    """Jointly generate the samples A and B in a sequential way."""
    click.echo("Joint generation...")
    n_generated_programs = config["n_generated_programs"]

    # load the generator objects for the two samples
    generators = [
        eval(benchmark_config[sample_name]["generation_object"])(
            out_folder=get_benchmark_folder(
                    config, benchmark_name, "programs", sample_name))
        for sample_name in ['sample_a', 'sample_b']
    ]

    for i in range(n_generated_programs):
        # sample a number of qubits
        n_qubits = random.randint(config["min_n_qubits"], config["max_n_qubits"])
        # create the program and store them automatically
        for generator in generators:
            generator.generate(
                n_qubits=n_qubits,
                n_ops_range=(config["min_n_ops"], config["max_n_ops"]),
                gate_set=config["gate_set"],
                random_seed=config["random_seed"],
                circuit_id=str(i))

def joined_execution(benchmark_name: str, benchmark_config: Dict[str, Any], config: Dict[str, Any]):
    """Jointly execute the programs A and B in a sequential way."""
    click.echo("Joint execution...")
    # get all qasm files in the respective folders


    # load the generator objects for the two samples
    generators = [
        eval(benchmark_config[sample_name]["execution_object"])(
            out_folder=get_benchmark_folder(
                    config, benchmark_name, "executions", sample_name))
        for sample_name in ['sample_a', 'sample_b']
    ]

    for i in range(n_generated_programs):
        # sample a number of qubits
        n_qubits = random.randint(config["min_n_qubits"], config["max_n_qubits"])
        # create the program and store them automatically
        for generator in generators:
            generator.generate(
                n_qubits=n_qubits,
                n_ops_range=(config["min_n_ops"], config["max_n_ops"]),
                gate_set=config["gate_set"],
                random_seed=config["random_seed"],
                circuit_id=str(i))




def single_generation(benchmark_config: Dict[str, Any], config: Dict[str, Any]):
    """"Generate the samples A or B separately."""
    click.echo("Single generation...")


def create_benchmark(config: Dict[str, Any]):
    """Create a benchmark from the given config file."""
    click.echo("Creating benchmark...")

    benchmarks = config["benchmarks_configurations"]

    check_folder_structure(config)

    for benchmark in benchmarks[:1]:
        b_name = benchmark['name']
        click.echo(f"Benchmark: {b_name}")
        # check that the benchmark has the right keys
        keys = benchmark.keys()
        required_keys = [
            "description", "title", "sample_a", "sample_b",
            "expected_divergence", "samples_relationship"
        ]
        for req_key in required_keys:
            assert req_key in keys, f"Benchmark missing key: {req_key}"

        samples_relationship = benchmark["samples_relationship"]

        # sample generation
        joined_generation(b_name, benchmark, config)

        # sample execution
        #joined_execution(name, benchmark, config_file)

        # run the two executors (in sequence because easier to debug)



def run_benchmark(config_file: Dict[str, Any]):
    """Run the benchmark from the given config file."""
    click.echo("Running benchmark...")


@click.group()
def cli():
    pass


@cli.command()
@click.argument('config_file')
def create(config_file):
    # check that there is a file at the config file location
    assert os.path.isfile(config_file), "Config file does not exist."
    # load the config file with yaml
    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    # check that the config file has the right keys
    keys = config.keys()
    required_keys = [
        "min_n_qubits",
        "max_n_qubits",
        "n_generated_programs",
        "fixed_sample_size"
        ]
    for req_key in required_keys:
        assert req_key in keys, f"Config file missing key: {req_key}"

    click.echo('Create benchmark')
    create_benchmark(config)


@cli.command()
@click.argument('config_file')
def run(config_file):
    click.echo('Run benchmark')
    #run_benchmark(config)


if __name__ == '__main__':
    cli()
