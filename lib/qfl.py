"""
Quantum Fuzzy Lop (QFL)

This tool fuzz quantum circuits in QASM and run them on multiple platforms.

Programming Mantra:
- every function should have 3-5 lines + return statement.
- max one if per function (which gives +3 lines to use).
"""
import random
import click
import multiprocessing
import time
from typing import Dict, List, Tuple, Any
import json
from os.path import join
import uuid

from utils import break_function_with_timeout
from utils import load_config_and_check
from utils import create_folder_structure
from utils import convert_single_program
from utils import run_single_program_in_memory

from generation_strategy import WeightedRandomCircuitGenerator
from detectors import *

# LEVEL - EXTRA

def estimate_n_samples_needed(
        n_measured_qubits: int = 1,
        user_defined_threshold: float = 0.5,
        confidence_level: float = 1.0,
        platform: str = None,
        backend: str = None):
    """Estimate the number of samples needed for a reliable comparison."""
    return 8192


def dump_metadata(
        metadata: Dict[str, Any] = None,
        metadata_filepath: str = None,
        to_indent: bool = False):
    """Dump the metadata dictionary to JSON."""
    with open(metadata_filepath, 'w') as f:
        if to_indent:
            json.dump(metadata, f, indent=4)
        else:
            json.dump(metadata, f)


def dump_all_metadata(
        experiment_folder, program_id, qasm, plat_a, plat_b, exec, div):
    """Dump all metadata."""
    all_metadata = {
        "program_id": program_id,
        "qasm": qasm,
        "platform_A": plat_a,
        "platform_B": plat_b,
        "divergence": div
    }
    dump_metadata(
        all_metadata,
        join(experiment_folder, "programs", "metadata", f"{program_id}.json"),
        to_indent=True)
    dump_metadata(
        exec,
        join(experiment_folder, "programs", "metadata", f"{program_id}_exec.json"))


# LEVEL 3

def detect_divergence(exec_metadata, detectors: List[Dict[str, Any]] = None):
    """Detect divergence with all the detectors and save the results."""
    results = {}
    for detector_config in detectors:
        detector_name = detector_config["name"]
        detector = eval(detector_config["detector_object"])()
        stat, pval = detector.check(result_A=exec_metadata['res_A'], result_B=exec_metadata['res_B'])
        results[detector_name] = {"statistic": stat, "p-value": pval}
    return results


def execute_programs(
        config:  Dict[str, Any],
        program_id: str,
        metadata_qasm: Dict[str, Any],
        metadata_A: Dict[str, Any],
        metadata_B: Dict[str, Any]):
    """Execute the programs."""
    exec_metadata = {
        "res_A": run_single_program_in_memory(
            target_file=metadata_A["pypath"],
            python_path=config["python_path"]),
        "platform_A": metadata_A["platform_name"],
        "res_B": run_single_program_in_memory(
            target_file=metadata_B["pypath"],
            python_path=config["python_path"]),
        "platform_B": metadata_B["platform_name"],
    }
    return exec_metadata


def translate_to_platform_code(
        config: Dict[str, Any],
        program_id: str, metadata_qasm: Dict[str, Any] = None):
    """Translate the output file into a to platform code."""
    metadata = []
    for platform in config["platforms"]:
        dest_filepath = convert_single_program(
            target_program=metadata_qasm["qasm_filepath"],
            dest_folder=join(config["experiment_folder"], "programs", platform["name"]),
            dest_format=platform["format"],
            qconvert_path=config["qconvert_path"],
        )
        metadata.append({"pypath": dest_filepath, "platform_name": platform["name"]})
    return metadata


def fuzz_qasm_program(
        experiment_folder: str = None,
        config_generation: Dict[str, Any] = None,
        feedback=None):
    """Fuzz a quantum circuit in QASM according to the given strategy."""
    program_id = uuid.uuid4().hex
    generator = eval(config_generation["generator_object"])(
        out_folder=join(experiment_folder, "programs", "qasm"),
        benchmark_name=f"seed_{config_generation['random_seed']}")
    _, metadata = generator.generate(
        n_qubits=random.randint(
            config_generation["min_n_qubits"],
            config_generation["max_n_qubits"]),
        n_ops_range=(
            config_generation["min_n_ops"], config_generation["max_n_ops"]),
        gate_set=config_generation["gate_set"],
        random_seed=config_generation["random_seed"],
        circuit_id=program_id)
    metadata = {
        'program_id': program_id,
        'qasm_filepath': join(experiment_folder, "programs", "qasm", f"{program_id}.qasm"),
        **metadata
    }
    return program_id, metadata

# LEVEL 2:


def loop(config):
    """Start fuzzing loop."""
    for i in range(5):
        print(f"Tick {i}")
        program_id, metadata_qasm = fuzz_qasm_program(
            experiment_folder=config["experiment_folder"],
            config_generation=config["generation_strategy"])
        print(f"Program {program_id}")
        metadata_A, metadata_B = translate_to_platform_code(
            config, program_id, metadata_qasm)
        exec_metadata = execute_programs(
            config, program_id, metadata_qasm, metadata_A, metadata_B)
        div_metadata = detect_divergence(exec_metadata, detectors=config["detectors"])
        dump_all_metadata(
            experiment_folder=config["experiment_folder"],
            program_id=program_id, qasm=metadata_qasm,
            plat_a=metadata_A, plat_b=metadata_B,
            exec=exec_metadata, div=div_metadata)
        print(f"Tock {i}")


# LEVEL 1:


def setup_environment(
        experiment_folder: str = None,
        folder_structure: str = None):
    """Setup the environment."""
    create_folder_structure(
        parent_folder=experiment_folder,
        structure=folder_structure)


def start_loop(
        config: Dict[str, Any] = None,
        budget_time: int = None):
    """Run the fuzzying loop."""
    if budget_time is not None:
        break_function_with_timeout(
            routine=loop,
            seconds_to_wait=budget_time,
            message="Change 'budget_time' in config yaml file.",
            args=(config,)
        )
    else:
        loop(config)


def debug_divergent_cases(
        max_runs_per_suspect_bug: int = 10,
        max_seconds_per_suspect_bug: int = 120):
    """Debug divergent cases."""
    pass


# LEVEL 0:


@click.command()
@click.argument('config_file')
def qml(config_file):
    """Run QFL."""
    config = load_config_and_check(config_file)
    setup_environment(
        experiment_folder=config["experiment_folder"],
        folder_structure=config["folder_structure"])
    start_loop(config, budget_time=config['budget_time'])
    debug_divergent_cases(
        max_runs_per_suspect_bug=config['max_runs_per_suspect_bug'],
        max_seconds_per_suspect_bug=config['max_seconds_per_suspect_bug'],
    )


if __name__ == '__main__':
    qml()
