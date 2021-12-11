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
import shutil

from detectors import *
from generation_strategy import *
from simulators import *
from simulators_mockup import *

from typing import Dict, Any, List


def load_json(filename, folder):
    """
    Read the json file at the given path.
    """
    with open(os.path.join(folder, filename), 'r') as f:
        return json.load(f)


def iterate_over(folder, filetype, parse_json=False):
    """
    Iterate over the files in the given folder.
    """
    for file in os.listdir(folder):
        if file.endswith(filetype):
            # open the file and yield it
            with open(os.path.join(folder, file), 'r') as f:
                if parse_json and filetype == '.json':
                    # read json file
                    file_content = json.load(f)
                else:
                    # read any other file
                    file_content = f.read()
                f.close()
            filename_without_extension = file.replace(filetype, "")
            yield filename_without_extension, file_content


def iterate_parallel(folder_master, folder_slave, filetype, parse_json=False):
    """
    Iterate over the files in the given folder.
    """
    for file in os.listdir(folder_master):
        if file.endswith(filetype):
            filename_without_extension = file.replace(filetype, "")
            result_tuple = []
            result_tuple.append(filename_without_extension)
            for folder in [folder_master, folder_slave]:
                # open the file and yield it
                with open(os.path.join(folder, file), 'r') as f:
                    if parse_json and filetype == '.json':
                        # read json file
                        file_content = json.load(f)
                    else:
                        # read any other file
                        file_content = f.read()
                    f.close()
                    result_tuple.append(file_content)
            yield result_tuple


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
            if stage_folder in ["programs", "executions"]:
                for sample_name in ["sample_a", "sample_b"]:
                    Path(os.path.join(subfolder, stage_folder, sample_name)).mkdir(
                        parents=True, exist_ok=True)
    click.echo("Folder structure checked and ready.")


def get_benchmark_folder(config: Dict[str, Any], benchmark_name: str, stage: str, sample: str = None) -> str:
    """Get the benchmark folder from the config file."""
    assert stage in ["programs", "executions", "ground_truth", "predictions"]
    assert benchmark_name in [b["name"] for b in config["benchmarks_configurations"]]
    if sample is not None:
        assert sample in ["sample_a", "sample_b"]
        return os.path.join(config["folder_benchmark"], benchmark_name, stage, sample)
    return os.path.join(config["folder_benchmark"], benchmark_name, stage)


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

    random.seed(config["random_seed"])
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


def generate_once_and_copy(benchmark_name: str, benchmark_config: Dict[str, Any], config: Dict[str, Any]):
    """Generate the samples A and copy the same in sample B."""
    click.echo("Generate Once&Copy generation...")
    n_generated_programs = config["n_generated_programs"]

    # load the generator objects for the two samples
    generator = eval(benchmark_config["generation_object"])(
            out_folder=get_benchmark_folder(
                    config, benchmark_name, "programs", 'sample_a'))

    random.seed(config["random_seed"])
    for i in range(n_generated_programs):
        # sample a number of qubits
        n_qubits = random.randint(config["min_n_qubits"], config["max_n_qubits"])
        # create the program and store them automatically
        generator.generate(
            n_qubits=n_qubits,
            n_ops_range=(config["min_n_ops"], config["max_n_ops"]),
            gate_set=config["gate_set"],
            random_seed=config["random_seed"],
            circuit_id=str(i))

    # copy the generated programs to the other sample
    source_folder = get_benchmark_folder(
        config, benchmark_name, "programs", 'sample_a')
    folder_other_sample = get_benchmark_folder(
        config, benchmark_name, "programs", 'sample_b')

    # copy the files
    for file in os.listdir(source_folder):
        shutil.copy(os.path.join(source_folder, file), folder_other_sample)


def joined_execution(benchmark_name: str, benchmark_config: Dict[str, Any], config: Dict[str, Any]):
    """Jointly execute the programs A and B in a sequential way."""
    click.echo("Joint execution...")

    n_shots = config["fixed_sample_size"]
    # load the generator objects for the two samples
    executors = [
        (
            get_benchmark_folder(
                config, benchmark_name, "programs", sample_name),
            eval(benchmark_config[sample_name]["execution_object"])(
                repetitions=n_shots),
            get_benchmark_folder(
                config, benchmark_name, "executions", sample_name),
        )
        for sample_name in ['sample_a', 'sample_b']
    ]

    # use the executors sequentially
    for program_folder, executor, out_folder in executors:

        for circuit_id, qasm_content in iterate_over(program_folder, ".qasm"):
            # load the program
            executor.from_qasm(qasm_content)
            # execute the program
            executor.execute(n_shots)
            result = executor.get_result()
            with open(os.path.join(out_folder, f"{circuit_id}.json"), "w") as execution_file:
                print(f"Saving execution of: {circuit_id}.json")
                json.dump(result, execution_file)


def create_benchmark(config: Dict[str, Any]):
    """Create a benchmark from the given config file."""
    click.echo("Creating benchmark...")

    benchmarks = config["benchmarks_configurations"]

    check_folder_structure(config)

    for benchmark in benchmarks[:2]:
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
        if samples_relationship == "identical":
            generate_once_and_copy(b_name, benchmark, config)
        elif samples_relationship == "independent":
            joined_generation(b_name, benchmark, config)

        # run the two executors (in sequence because easier to debug)
        joined_execution(b_name, benchmark, config)

        # create the ground truth
        ground_truth_folder = get_benchmark_folder(
            config, b_name, "ground_truth")
        record = {"ground_truth": benchmark["expected_divergence"]}
        for i in range(config["n_generated_programs"]):
            # save json file with record
            with open(os.path.join(ground_truth_folder, f"{i}.json"), "w") as f:
                json.dump(record, f)


def run_benchmark(config: Dict[str, Any]):
    """Run the benchmark from the given config file."""
    click.echo("Running benchmark...")

    detectors = []
    if "ks" in config["detectors"]:
        detectors.append(KS_Detector())

    benchmarks = config["benchmarks_configurations"]

    check_folder_structure(config)

    for benchmark in benchmarks[:2]:
        b_name = benchmark['name']

        click.echo(f"Benchmark: {b_name}")

        prediction_folder = get_benchmark_folder(
            config, b_name, "predictions")

        exec_folder_A = get_benchmark_folder(
                config, b_name, "executions", 'sample_a')
        exec_folder_B = get_benchmark_folder(
                config, b_name, "executions", 'sample_b')
        print(f"Prediction folder: {prediction_folder}")
        print(f"Execution folder A: {exec_folder_A}")
        print(f"Execution folder B: {exec_folder_B}")
        for name, res_a, res_b in iterate_parallel(exec_folder_A, exec_folder_B, filetype=".json", parse_json=True):
            for detector in detectors:
                detector_prediction_folder = \
                    os.path.join(prediction_folder, detector.name)
                Path(detector_prediction_folder).mkdir(
                    parents=True, exist_ok=True)
                statistic, p_value = detector.check(res_a, res_b)
                comparison = {
                    "statistic": statistic,
                    "p_value": p_value,
                    "test": detector.name,
                }
                with open(os.path.join(detector_prediction_folder, name + ".json"), "w") as file:
                    json.dump(comparison, file)
                    file.close()


@click.group()
def cli():
    pass


def load_config_and_check(config_file: str, required_keys: List[str]):
    """Load the config file and check that it has the right keys."""
    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    for key in required_keys:
        assert key in config.keys(), f"Missing key: {key}"
    return config


@cli.command()
@click.argument('config_file')
def create(config_file):
    config = load_config_and_check(config_file, [
        "min_n_qubits",
        "max_n_qubits",
        "n_generated_programs",
        "fixed_sample_size"
        ])

    click.echo('Create benchmark')
    create_benchmark(config)


@cli.command()
@click.argument('config_file')
def run(config_file):
    config = load_config_and_check(config_file, [
        "detectors"
        ])
    click.echo('run benchmark')
    run_benchmark(config)


if __name__ == '__main__':
    cli()
