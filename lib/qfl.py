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
from timeit import default_timer as timer
from typing import Dict, List, Tuple, Any
import json
from os.path import join
import uuid
import pandas as pd

from lib.utils import break_function_with_timeout
from lib.utils import load_config_and_check
from lib.utils import create_folder_structure
from lib.utils import convert_single_program
from lib.utils import run_single_program_in_memory

from lib.utils_db import get_database_connection
from lib.utils_db import update_database
from lib.utils_db import get_program_ids_in_table

import lib.generation_strategy
from lib.generation_strategy import *
from lib.detectors import *
from lib.tket_interface import convert_and_execute_qiskit_and_cirq_via_tket
from lib.multi_platform_interface import convert_and_execute_qiskit_and_cirq_natively


from math import sqrt


# LEVEL - EXTRA

def estimate_n_samples_needed(
        config: Dict[str, Any],
        n_measured_qubits: int = 1,
        platform: str = None,
        backend: str = None):
    """Estimate the number of samples needed for a reliable comparison."""
    # based on the key strategy_sample_size_estimation
    if config["strategy_sample_size_estimation"] is None:
        return config["fixed_sample_size"]
    elif config["strategy_sample_size_estimation"] == "qdiff":
        user_defined_threshold = config["qdiff_user_defined_threshold"]
        confidence_level = config["qdiff_confidence_level"]
        n_quantum_states = 2**n_measured_qubits
        return int((1 / sqrt(1 - confidence_level)) * sqrt(n_quantum_states) * (user_defined_threshold)**(-2))


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
        out_folder, program_id, qasm, exec, div, **kwargs):
    """Dump all metadata."""
    all_metadata = {
        "program_id": program_id,
        "qasm": qasm,
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


def scan_for_divergence(config: Dict[str, Any], test_name: str = 'ks',
                        alpha_level: int = 0.05, method="holm"):
    """Scan for divergence in the table."""
    con = get_database_connection(config, "qfl.db")
    df = pd.read_sql("SELECT * FROM QFLDATA", con)
    pval_col = f"divergence.{test_name}.p-value"
    df_sorted_pvals = df.sort_values(by=[pval_col])
    k = len(df_sorted_pvals)
    i_star = None
    for i, (idx, row) in enumerate(df_sorted_pvals.iterrows()):
        ordinal_i = i + 1
        P_i = row[pval_col]
        if method == 'holm':
            threshold = alpha_level / (k - ordinal_i + 1)
        elif method == 'bonferroni':
            threshold = alpha_level / (k)
        elif method == 'bh':
            threshold = (alpha_level / (k)) * ordinal_i
        # print(f"(i: {ordinal_i}) current p-value: {P_i} vs threshold: {threshold}")
        if P_i > threshold:
            i_star = i
            print(f"i*: {i_star}")
            break
    if i_star is None:
        df_divergent = df_sorted_pvals
    else:
        df_divergent = df_sorted_pvals.iloc[:i_star]
    all_program_ids = get_program_ids_in_table(con, table_name='DIVERGENCE')
    new_df_divergent = df_divergent[
        ~df_divergent["program_id"].isin(all_program_ids)]
    if len(new_df_divergent) > 0:
        print(f"{len(new_df_divergent)} new divergent programs found.")
        print(new_df_divergent)
        for record in new_df_divergent.to_dict(orient='records'):
            update_database(con, "DIVERGENCE", record)
    con.close()


def detect_divergence(exec_metadata, detectors: List[Dict[str, Any]] = None):
    """Detect divergence with all the detectors and save the results."""
    results = {}
    for detector_config in detectors:
        detector_name = detector_config["name"]
        start_check = timer()
        detector = eval(detector_config["detector_object"])()
        stat, pval = detector.check(result_A=exec_metadata['res_A'], result_B=exec_metadata['res_B'])
        end_check = timer()
        time_check = end_check - start_check
        results[detector_name] = {"statistic": stat, "p-value": pval, "time": time_check}
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
        generator: lib.generation_strategy.GenerationStrategy,
        experiment_folder: str = None,
        config_generation: Dict[str, Any] = None,
        feedback=None):
    """Fuzz a quantum circuit in QASM according to the given strategy."""
    program_id = uuid.uuid4().hex
    selected_gate_set = config_generation["gate_set"]
    if config_generation["gate_set_dropout"] is not None:
        dropout = config_generation["gate_set_dropout"]
        selected_gate_set = list(np.random.choice(selected_gate_set,
            size=int(len(selected_gate_set) * dropout), replace=False))
    _, metadata = generator.generate(
        n_qubits=random.randint(
            config_generation["min_n_qubits"],
            config_generation["max_n_qubits"]),
        n_ops_range=(
            config_generation["min_n_ops"], config_generation["max_n_ops"]),
        gate_set=selected_gate_set,
        circuit_id=program_id)
    metadata = {
        'program_id': program_id,
        'selected_gate_set': [g["name"] for g in selected_gate_set],
        'qasm_filepath': join(experiment_folder, "programs", "qasm", f"{program_id}.qasm"),
        **metadata
    }
    return program_id, metadata


def execute_qasm_program(
        config:  Dict[str, Any],
        program_id: str,
        metadata_qasm: Dict[str, Any]):
    """Execute the QASM program."""
    if config["mode"] == "qconvert":
        metadata_A, metadata_B = translate_to_platform_code(
            config, program_id, metadata_qasm)
        exec_metadata = execute_programs(
            config, program_id, metadata_qasm, metadata_A, metadata_B)
    elif config["mode"] == "tket":
        results = convert_and_execute_qiskit_and_cirq_via_tket(
            qasm_path=metadata_qasm["qasm_filepath"],
            shots=estimate_n_samples_needed(
                config, n_measured_qubits=metadata_qasm["n_qubits"])
        )
        exec_metadata = {
            "res_A": results["qiskit"],
            "platform_A": "qiskit",
            "res_B": results["cirq"],
            "platform_B": "cirq",
            "profile_output": results["profile_output"],
            "profile_function_calls": results["profile_function_calls"],
            "profile_time": results["profile_time"]
        }
    elif config["mode"] == "native":
        results = convert_and_execute_qiskit_and_cirq_natively(
            qasm_path=metadata_qasm["qasm_filepath"],
            shots=estimate_n_samples_needed(
                config, n_measured_qubits=metadata_qasm["n_qubits"])
        )
        exec_metadata = {
            "res_A": results["qiskit"],
            "platform_A": "qiskit",
            "res_B": results["cirq"],
            "platform_B": "cirq"
        }
    return exec_metadata


# LEVEL 2:


def loop(config):
    """Start fuzzing loop."""
    config_generation = config["generation_strategy"]
    experiment_folder = config["experiment_folder"]
    generator = eval(config_generation["generator_object"])(
        out_folder=join(experiment_folder, "programs", "qasm"),
        benchmark_name=f"seed_{config_generation['random_seed']}",
        random_seed=config_generation["random_seed"])
    while True:
        program_id, metadata_qasm = fuzz_qasm_program(
            generator,
            experiment_folder=experiment_folder,
            config_generation=config["generation_strategy"])
        exec_metadata = execute_qasm_program(
            config, program_id, metadata_qasm)
        div_metadata = detect_divergence(exec_metadata, detectors=config["detectors"])
        all_metadata = dump_all_metadata(
            out_folder=join(experiment_folder, "programs", "metadata"),
            program_id=program_id, qasm=metadata_qasm,
            exec=exec_metadata, div=div_metadata,
            platform_names=[p["name"] for p in config["platforms"]],
            shots=estimate_n_samples_needed(
                config, n_measured_qubits=metadata_qasm["n_qubits"]))
        con = get_database_connection(config, "qfl.db")
        update_database(con, table_name="QFLDATA", record=all_metadata)
        scan_for_divergence(config,
                            method=config["divergence_threshold_method"],
                            test_name=config["divergence_primary_test"],
                            alpha_level=config["divergence_alpha_level"])

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


if __name__ == '__main__':
    qml()
