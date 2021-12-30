
import click
import os
from utils import iterate_parallel, load_config_and_check
from utils import iterate_parallel_n
from utils import iterate_over
from pathlib import Path
import random

from typing import Any, Dict
from generation_strategy import *
import subprocess
import sys
import json

from itertools import combinations

from detectors import *
from utils import convert
from utils import run_programs
from utils import iterate_over_program_ids
from utils import iterate_over_pairs_of_group



def replace_in_all_files(folder, detect_string, substitute_string):
    """Replace the given string in all the files in the folder."""
    for circuit_id, content in iterate_over(folder, filetype=".py", parse_json=False):
        content = content.replace(detect_string, substitute_string)
        with open(os.path.join(folder, circuit_id + ".py"), "w") as f:
            f.write(content)
            f.close()



def get_folder(config, comparison_name, stage, compiler_name=None):
    if compiler_name is None:
        return os.path.join(
            config["experiment_folder"], comparison_name, stage)
    return os.path.join(
        config["experiment_folder"], comparison_name, stage, compiler_name)


def prepare_folders(config: Dict[str, Any], benchmark_mode: bool) -> None:
    """Prepare the folders."""
    click.echo("Checking folder structure...")
    comparisons = config["comparisons"]
    experiment_folder = config["experiment_folder"]
    Path(experiment_folder).mkdir(parents=True, exist_ok=True)
    for comparison in comparisons:
        if benchmark_mode and not comparison.get("is_benchmark", False):
            print("Skipping folder creation: ", comparison["name"])
            print("[Not part of the benchmark.]")
            continue
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


def generate_and_run_programs(config: Dict[str, Any], benchmark_mode: bool) -> None:
    """Generate and run the programs."""

    prepare_folders(config, benchmark_mode)

    for comparison in config["comparisons"]:

        if benchmark_mode and not comparison.get("is_benchmark", False):
            print("Skipping comparison: ", comparison["name"])
            print("[Not part of the benchmark.]")
            continue

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

        # GENERATE GROUND TRUTH

        if benchmark_mode and \
                "expected_divergence" in comparison.keys():
            print("Creating ground truth based on expected divergence:",
                  comparison["name"])
            # create the ground truth
            ground_truth_folder = get_folder(
                config, comparison["name"], "ground_truth")
            record = {
                "expected_divergence": comparison["expected_divergence"]}
            # create ground truth
            # based on the number of generated programs in the QASM folder
            generated_qasms_filenames = [
                f.replace(".qasm", "") for f in os.listdir(get_folder(
                    config, comparison["name"], "original_programs"))
                if f.endswith(".qasm")
            ]
            for i in generated_qasms_filenames:
                # save json file with record
                record["circuit_id"] = str(i)
                record["benchmark_name"] = comparison["name"]
                with open(os.path.join(ground_truth_folder, f"{i}.json"), "w") as f:
                    json.dump(record, f)

        # CREATE COMPILER-SPECIFIC PROGRAMS (CIRC, QISKIT, PYQUIL)

        compilers = comparison["compilers"]
        for compiler in compilers:

            compiler_name = compiler["name"]

            compiler_specific_folder = get_folder(
                config, comparison["name"], "programs", compiler_name)

            convert(source_folder=get_folder(
                        config, comparison["name"], "original_programs"),
                    dest_folder=compiler_specific_folder,
                    dest_format=compiler_name,
                    qconvert_path=config["qconvert_path"])

            # REPLACE THE NUMBER OF SHOTS
            replace_in_all_files(
                folder=get_folder(
                    config, comparison["name"], "programs", compiler_name),
                detect_string=compiler["shots_lookup"],
                substitute_string=compiler["shots_substitute"].format(
                    injected_shot=config["fixed_sample_size"]))

            # EXECUTE PROGRAMS
            run_programs(
                source_folder=compiler_specific_folder,
                dest_folder=get_folder(
                        config, comparison["name"], "executions", compiler_name),
                python_path=config["python_path"],
                n_executions=config["n_executions"])


def detect_divergence(config: Dict[str, Any], benchmark_mode: bool) -> None:
    """Detect the divergence."""

    detectors = config["detectors"]

    for detector in detectors:
        print("-" * 80)
        print("Running detector:", detector["name"])
        detector_object = eval(detector["detector_object"])()
        for comparison in config["comparisons"]:

            if benchmark_mode and not comparison.get("is_benchmark", False):
                print("Skipping detection: ", comparison["name"])
                print("[Not part of the benchmark.]")
                continue

            compiler_names = [
                compiler["name"] for compiler in comparison["compilers"]]

            random_seed = detector.get("random_seed", None)

            for program_id, group_same_program_id in iterate_over_program_ids(
                    execution_folder=get_folder(
                        config, comparison["name"], "executions"),
                    compilers_names=compiler_names):
                print("Circuit ID: ", program_id)
                print("-" * 80)
                # print("Elements in the group:", group_same_program_id)
                # print("-" * 80)

                # generate program-specific json output
                prediction = {
                    "test": detector["name"],
                    "test_long_name": detector["test_long_name"],
                    "comparison_name": comparison["name"],
                    "circuit_id": program_id,
                    "random_seed": random_seed
                }
                comparisons = []

                for path_exec_a, path_exec_b, res_A, res_B in iterate_over_pairs_of_group(group_same_program_id):
                    # print("res_a: ", len(res_A))
                    # print("res_b: ", len(res_B))
                    sorted_paths = sorted([path_exec_a, path_exec_b])
                    # ran detector

                    pair = {
                        "platform_a": sorted_paths[0].split("/")[-2],
                        "platform_b": sorted_paths[1].split("/")[-2],
                        "path_exec_a": sorted_paths[0],
                        "path_exec_b": sorted_paths[1]
                    }

                    try:
                        statistic, p_value = detector_object.check(res_A, res_B, random_seed)
                        pair[f"statistic"] = statistic
                        pair[f"p_value"] = p_value
                    except Exception as e:
                        prediction[f"statistic"] = 0
                        pair[f"p_value"] = -1
                        pair["exception"] = str(e)

                    comparisons.append(pair)

                # save detector result for this program_ID
                prediction["comparisons"] = comparisons

                # save file
                detector_pred_folder = get_folder(
                    config, comparison["name"], "predictions", detector["name"])
                Path(detector_pred_folder).mkdir(parents=True, exist_ok=True)
                with open(os.path.join(detector_pred_folder, program_id + ".json"), "w") as file:
                    json.dump(prediction, file)
                    file.close()


@click.group()
def cli():
    pass


@cli.command()
@click.argument('config_file')
@click.option('--benchmark', is_flag=True)
def generate(config_file, benchmark):
    config = load_config_and_check(config_file, [
        "min_n_qubits",
        "max_n_qubits",
        "n_generated_programs",
        "fixed_sample_size"
        ])

    click.echo('Generate and Run Programs')
    generate_and_run_programs(config, benchmark)


@cli.command()
@click.argument('config_file')
@click.option('--benchmark', is_flag=True)
def detect(config_file, benchmark):
    config = load_config_and_check(config_file, [
        "detectors"
        ])
    click.echo('Detect Divergence')
    detect_divergence(config, benchmark)


if __name__ == '__main__':
    cli()
