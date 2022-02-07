"""
Quantum Metamorphic Testing

This tool fuzz quantum circuits in Qiskit and run a follow-up circuit with
some relationship to the first circuit.

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
import pandas as pd

from utils import break_function_with_timeout
from utils import load_config_and_check
from utils import create_folder_structure
from utils import dump_metadata
from utils import convert_single_program
from utils import run_single_program_in_memory

from utils_db import get_database_connection
from utils_db import update_database
from utils_db import get_program_ids_in_table

from generation_strategy_python import *
from detectors import *

from math import sqrt


from qfl import estimate_n_samples_needed
from qfl import setup_environment
from qfl import scan_for_divergence
from qfl import detect_divergence


from metamorph import change_backend


def dump_all_metadata(
        out_folder, program_id, exec, div, **kwargs):
    """Dump all metadata."""
    all_metadata = {
        "program_id": program_id,
        "divergence": div,
        **kwargs
    }
    dump_metadata(
        all_metadata,
        join(out_folder, f"{program_id}.json"),
        to_indent=True)
    dump_metadata(
        exec,
        join(out_folder, f"{program_id}_exec.json"))
    return all_metadata


# LEVEL 3


def execute_single_py_program(filepath: str):
    """Execute a single python program."""
    py_content = open(filepath, "r").read()
    GLOBALS = {"RESULT": 0}
    exec(py_content, GLOBALS)
    return GLOBALS["RESULT"]


def fuzz_source_program(
        generator: Fuzzer,
        experiment_folder: str = None,
        config_generation: Dict[str, Any] = None,
        config: Dict[str, Any] = None,
        feedback=None):
    """Fuzz a quantum circuit in Qiskit according to the given strategy."""
    program_id = uuid.uuid4().hex
    selected_gate_set = config_generation["gate_set"]
    if config_generation["gate_set_dropout"] is not None:
        dropout = config_generation["gate_set_dropout"]
        selected_gate_set = list(np.random.choice(selected_gate_set,
            size=int(len(selected_gate_set) * dropout), replace=False))

    selected_optimizations = config_generation["optimizations"]
    if config_generation["optimizations_dropout"] is not None:
        dropout = config_generation["optimizations_dropout"]
        selected_optimizations = list(np.random.choice(selected_optimizations,
            size=int(len(selected_optimizations) * dropout), replace=False))

    n_qubits = random.randint(
            config_generation["min_n_qubits"],
            config_generation["max_n_qubits"])
    n_ops = random.randint(
            config_generation["min_n_ops"],
            config_generation["max_n_ops"])
    shots = estimate_n_samples_needed(
        config, n_measured_qubits=n_qubits)

    py_file_content, metadata = generator.generate_file(
        gate_set=selected_gate_set,
        n_qubits=n_qubits,
        n_ops=n_ops,
        optimizations=selected_optimizations,
        backend=np.random.choice(config_generation["backends"]),
        shots=shots)

    program_id = uuid.uuid4().hex
    py_file_path = join(experiment_folder, "programs", "source", f"{program_id}.py")
    with open(py_file_path, "w") as f:
        f.write(py_file_content)

    metadata = {
        'program_id': program_id,
        'selected_gate_set': [g["name"] for g in selected_gate_set],
        'selected_optimization': selected_optimizations,
        'shots': shots,
        'n_qubits': n_qubits,
        'n_ops': n_ops,
        'py_file_path': py_file_path,
        **metadata
    }
    return program_id, metadata


def execute_programs(
        metadata_source:  Dict[str, Any],
        metadata_followup: Dict[str, Any]):
    """Execute programs and return the metadata with results."""
    exceptions = {}
    try:
        res_a = execute_single_py_program(metadata_source["py_file_path"])
    except Exception as e:
        exceptions['exceptions_source'] = str(e)
        res_a = {"0": 1}
    try:
        res_b = execute_single_py_program(metadata_followup["py_file_path"])
    except Exception as e:
        exceptions['exceptions_followup'] = str(e)
        res_b = {"0": 1}
    if len(exceptions.items()) > 0:
        print("Crash found.")
    exec_metadata = {
        "res_A": res_a,
        "platform_A": "source",
        "res_B": res_b,
        "platform_B": "follow_up",
        **exceptions
    }
    return exec_metadata


def metamorph_backend(metadata: Dict[str, Any], config: Dict[str, Any]):
    """Change the backend of the passed pyfile."""
    filepath = metadata["py_file_path"]
    file_content = open(filepath, "r").read()
    metamorphed_file_content = change_backend(
        source_code=file_content,
        available_backends=config["generation_strategy"]["backends"])
    experiment_folder = config["experiment_folder"]
    program_id = metadata["program_id"]
    new_filepath = join(experiment_folder, "programs", "followup", f"{program_id}.py")
    with open(new_filepath, "w") as f:
        f.write(metamorphed_file_content)
    new_metadata = {**metadata}
    new_metadata["py_file_path"] = new_filepath
    return new_metadata


# LEVEL 2:


def loop(config):
    """Start fuzzing loop."""
    config_generation = config["generation_strategy"]
    experiment_folder = config["experiment_folder"]
    generator = eval(config_generation["generator_object"])()
    while True:
        program_id, metadata_source = fuzz_source_program(
            generator,
            experiment_folder=experiment_folder,
            config_generation=config["generation_strategy"],
            config=config)
        metadata_followup = metamorph_backend(metadata_source, config)
        exec_metadata = execute_programs(
            metadata_source=metadata_source,
            metadata_followup=metadata_followup)
        div_metadata = detect_divergence(exec_metadata, detectors=config["detectors"])
        all_metadata = dump_all_metadata(
            out_folder=join(experiment_folder, "programs", "metadata"),
            program_id=program_id, source=metadata_source, followup=metadata_followup,
            exec=exec_metadata, div=div_metadata)
        con = get_database_connection(config, "qfl.db")
        update_database(con, table_name="QFLDATA", record=all_metadata)
        scan_for_divergence(config,
                            method=config["divergence_threshold_method"],
                            test_name=config["divergence_primary_test"],
                            alpha_level=config["divergence_alpha_level"])

# LEVEL 1:


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


# LEVEL 0:


@click.command()
@click.argument('config_file')
def qmtl(config_file):
    """Run Quantum Metamorphic Testing loop."""
    config = load_config_and_check(config_file)
    setup_environment(
        experiment_folder=config["experiment_folder"],
        folder_structure=config["folder_structure"])
    start_loop(config, budget_time=config['budget_time'])


if __name__ == '__main__':
    qmtl()
