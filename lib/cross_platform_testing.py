
import click
import os
from utils import iterate_parallel, load_config_and_check
from utils import iterate_parallel_n
from pathlib import Path
import random

from typing import Any, Dict
from generation_strategy import *
import subprocess
import sys
import json

from itertools import combinations

from detectors import *


def get_folder(config, comparison_name, stage, compiler_name=None):
    if compiler_name is None:
        return os.path.join(
            config["experiment_folder"], comparison_name, stage)
    return os.path.join(
        config["experiment_folder"], comparison_name, stage, compiler_name)


def prepare_folders(config: Dict[str, Any]) -> None:
    """Prepare the folders."""
    click.echo("Checking folder structure...")
    comparisons = config["comparisons"]
    experiment_folder = config["experiment_folder"]
    Path(experiment_folder).mkdir(parents=True, exist_ok=True)
    for comparison in comparisons:
        comparison_name = comparison["name"]
        compilers = comparison["compilers"]
        subfolder = os.path.join(experiment_folder, comparison_name)
        Path(subfolder).mkdir(parents=True, exist_ok=True)
        for stage_folder in ["programs", "executions", "ground_truth", "predictions"]:
            Path(os.path.join(subfolder, stage_folder)).mkdir(
                parents=True, exist_ok=True)
            if stage_folder in ["programs", "executions"]:
                for compiler in compilers:
                    Path(os.path.join(subfolder, stage_folder, compiler["name"])).mkdir(
                        parents=True, exist_ok=True)
        Path(os.path.join(subfolder, "original_programs")).mkdir(
                        parents=True, exist_ok=True)
    click.echo("Folder structure checked and ready.")


def run_programs(source_folder, dest_folder, python_path=None):
    if python_path is None:
        raise ValueError("python_path must be specified")
    files = os.listdir(source_folder)
    py_files = [f for f in files if f.endswith(".py")]
    for filename in py_files:
        prefix = filename.split("_")[0]
        print(f"Executing: {filename}")
        with open(os.path.join(dest_folder, prefix + ".json"), 'w') as output_file:
            script_to_execute = os.path.join(source_folder, filename)
            proc = subprocess.Popen(
                [python_path, script_to_execute],
                stdout=subprocess.PIPE)
            output = str(proc.stdout.read().decode('unicode_escape'))
            output = output.replace("'", '"')
            res = json.loads(output)
            print(res)
            json.dump(res, output_file)


def convert(source_folder, dest_folder, dest_format="pyquil", qconvert_path=None):
    if qconvert_path is None:
        raise ValueError("qconvert_path must be specified")
    files = os.listdir(source_folder)
    qasm_files = [f for f in files if f.endswith(".qasm")]
    print(qasm_files)
    for filename in qasm_files:
        src_filepath = os.path.join(source_folder, filename)
        dest_filepath = os.path.join(dest_folder, filename.replace(".qasm", "_" + dest_format) + ".py")
        string_to_execute = f"{qconvert_path} -h -s qasm -d {dest_format} -i {src_filepath} -o {dest_filepath}"
        print(string_to_execute)
        os.system(string_to_execute)


def generate_and_run_programs(config: Dict[str, Any]) -> None:
    """Generate and run the programs."""

    prepare_folders(config)

    for comparison in config["comparisons"]:

        # GENERATE QASM PROGRAMS

        generator = eval(comparison["generation_object"])(
            out_folder=get_folder(
                config, comparison["name"], "original_programs"),
            benchmark_name=comparison["name"]
        )

        n_generated_programs = config["n_generated_programs"]

        random.seed(config["random_seed"])
        for i in range(n_generated_programs):
            # sample a number of qubits
            n_qubits = random.randint(config["min_n_qubits"], config["max_n_qubits"])
            # create the program and store them automatically
            try:
                generator.generate(
                    n_qubits=n_qubits,
                    n_ops_range=(config["min_n_ops"], config["max_n_ops"]),
                    gate_set=config["gate_set"],
                    random_seed=config["random_seed"],
                    circuit_id=str(i))
            except NoMoreProgramsAvailable:
                break

        # CREATE COMPILER-SPECIFIC PROGRAMS (CIRC, QISKIT, PYQUIL)

        compilers = comparison["compilers"]
        compiler_names = [compiler["name"] for compiler in compilers]
        for compiler_name in compiler_names:

            compiler_specific_folder = get_folder(
                config, comparison["name"], "programs", compiler_name)

            convert(source_folder=get_folder(
                        config, comparison["name"], "original_programs"),
                    dest_folder=compiler_specific_folder,
                    dest_format=compiler_name,
                    qconvert_path=config["qconvert_path"])

            # EXECUTE PROGRAMS
            run_programs(
                source_folder=compiler_specific_folder,
                dest_folder=get_folder(
                        config, comparison["name"], "executions", compiler_name),
                python_path=config["python_path"])


def detect_divergence(config: Dict[str, Any]) -> None:
    """Detect the divergence."""

    detectors = config["detectors"]

    for detector in detectors:
        print("-" * 80)
        print("Running detector:", detector["name"])
        detector_object = eval(detector["detector_object"])()
        for comparison in config["comparisons"]:

            compiler_names = [compiler["name"] for compiler in comparison["compilers"]]

            random_seed = detector.get("random_seed", None)

            compiler_folders = [
                get_folder(config, comparison["name"], "executions", compiler_name)
                for compiler_name in compiler_names
            ]

            for (circuit_id, *compiler_results) in iterate_parallel_n(folders=compiler_folders, filetype='.json', parse_json=True):
                print("Analyzing circuit: ", circuit_id)
                print(len(compiler_results))

                prediction = {
                    "test": detector["name"],
                    "test_long_name": detector["test_long_name"],
                    "comparison_name": comparison["name"],
                    "circuit_id": circuit_id,
                    "random_seed": random_seed
                }

                named_results = zip(compiler_names, compiler_results)
                differential_pairs = combinations(named_results, 2)
                alarm_pairs = []

                for ((name_A, res_A), (name_B, res_B)) in differential_pairs:
                    sorted_compilers = sorted([name_A, name_B])
                    pair_name = f"{sorted_compilers[0]}_{sorted_compilers[1]}"
                    print("Comparing: ", pair_name)

                    try:
                        statistic, p_value = detector_object.check(res_A, res_B, random_seed)
                        prediction[f"statistic_{pair_name}"] = statistic
                        prediction[f"p_value_{pair_name}"] = p_value
                    except Exception as e:
                        prediction[f"statistic_{pair_name}"] = 0
                        prediction[f"p_value_{pair_name}"] = -1
                        prediction["exception"] = str(e)

                # save file
                detector_pred_folder = get_folder(
                    config, comparison["name"], "predictions")
                with open(os.path.join(detector_pred_folder, circuit_id + ".json"), "w") as file:
                    json.dump(prediction, file)
                    file.close()



@click.group()
def cli():
    pass


@cli.command()
@click.argument('config_file')
def generate(config_file):
    config = load_config_and_check(config_file, [
        "min_n_qubits",
        "max_n_qubits",
        "n_generated_programs",
        "fixed_sample_size"
        ])

    click.echo('Generate and Run Programs')
    generate_and_run_programs(config)


@cli.command()
@click.argument('config_file')
def detect(config_file):
    config = load_config_and_check(config_file, [
        "detectors"
        ])
    click.echo('Detect Divergence')
    detect_divergence(config)


if __name__ == '__main__':
    cli()
