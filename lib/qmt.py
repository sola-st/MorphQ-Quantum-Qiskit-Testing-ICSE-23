"""
Quantum Metamorphic Testing

This tool fuzz quantum circuits in Qiskit and run a follow-up circuit with
some relationship to the first circuit.

Programming Mantra:
- every function should have 3-5 lines + return statement.
- max one if per function (which gives +3 lines to use).
"""
from datetime import datetime
import os
from os.path import join
import json
from math import sqrt
import multiprocessing
import time
from timeit import default_timer as timer
from typing import Dict, List, Tuple, Any, Callable
import random
import uuid
import traceback

import click
import coverage
from coverage import Coverage
import pandas as pd
from termcolor import colored


from lib.utils import break_function_with_timeout
from lib.utils import load_config_and_check
from lib.utils import create_folder_structure
from lib.utils import dump_metadata
from lib.utils import convert_single_program
from lib.utils import run_single_program_in_memory
from lib.utils import iterdict_types

from lib.utils_db import get_database_connection
from lib.utils_db import update_database
from lib.utils_db import get_program_ids_in_table

from lib.generation_strategy_python import *
from lib.detectors import *

from lib.qfl import estimate_n_samples_needed
from lib.qfl import setup_environment
from lib.qfl import scan_for_divergence
from lib.qfl import detect_divergence

from lib.metamorph import *
from lib.metamorph import MetamorphicRelationship
from lib.metamorph import Pipeline

from lib.mr import MetamorphicTransformation
from lib.mr.chain import ChainedTransformation


def dump_all_metadata(
        out_folder, program_id, **kwargs):
    """Dump all metadata."""
    all_metadata = {
        "program_id": program_id,
        **kwargs
    }
    try:
        dump_metadata(
            all_metadata,
            join(out_folder, f"{program_id}.json"),
            to_indent=True)
    except Exception as e:
        print(all_metadata)
        iterdict_types(all_metadata)
        raise e
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
    start_generation = timer()
    program_id = uuid.uuid4().hex
    selected_gate_set = config_generation["gate_set"]
    if config_generation["gate_set_dropout"] is not None:
        dropout = config_generation["gate_set_dropout"]
        selected_gate_set = list(np.random.choice(
            selected_gate_set,
            size=int(len(selected_gate_set) * dropout),
            replace=False))

    selected_optimizations = config_generation["optimizations"]
    if config_generation["optimizations_dropout"] is not None:
        dropout = config_generation["optimizations_dropout"]
        selected_optimizations = list(np.random.choice(
            selected_optimizations,
            size=int(len(selected_optimizations) * dropout),
            replace=False))

    n_qubits = random.randint(
            config_generation["min_n_qubits"],
            config_generation["max_n_qubits"])
    n_ops = random.randint(
            config_generation["min_n_ops"],
            config_generation["max_n_ops"])
    opt_level = int(np.random.choice(config_generation["optimization_levels"]))
    target_gates = None

    shots = estimate_n_samples_needed(
        config, n_measured_qubits=n_qubits)

    py_file_content, metadata = generator.generate_file(
        gate_set=selected_gate_set,
        n_qubits=n_qubits,
        n_ops=n_ops,
        optimizations=selected_optimizations,
        backend=np.random.choice(config_generation["backends"]),
        shots=shots,
        level_auto_optimization=opt_level,
        target_gates=target_gates)

    program_id = uuid.uuid4().hex
    py_file_path = join(
        experiment_folder, "programs", "source", f"{program_id}.py")
    with open(py_file_path, "w") as f:
        f.write(py_file_content)
    end_generation = timer()
    time_generation = end_generation - start_generation
    metadata = {
        'program_id': program_id,
        'selected_gate_set': [g["name"] for g in selected_gate_set],
        'selected_optimization': selected_optimizations,
        'shots': shots,
        'n_qubits': n_qubits,
        'n_ops': n_ops,
        'opt_level': opt_level,
        'target_gates': target_gates,
        'py_file_path': py_file_path,
        'time_generation': time_generation,
        **metadata
    }
    return program_id, metadata


def execute_programs(
        metadata_source:  Dict[str, Any],
        metadata_followup: Dict[str, Any]):
    """Execute programs and return the metadata with results."""
    exceptions = {'source': None, 'followup': None}
    start_exec = timer()
    try:
        res_a = execute_single_py_program(metadata_source["py_file_path"])
    except Exception as e:
        exceptions['source'] = str(e)
        res_a = {"0": 1}
    try:
        res_b = execute_single_py_program(metadata_followup["py_file_path"])
    except Exception as e:
        exceptions['followup'] = str(e)
        res_b = {"0": 1}
    end_exec = timer()
    time_exec = end_exec - start_exec
    if len(exceptions.items()) > 0:
        color = 'red' if (
            exceptions['followup'] is not None or
            exceptions['source'] is not None) else 'green'
        print(colored(f"Exceptions from execution: {exceptions}", color))
    exec_metadata = {
        "res_A": res_a,
        "platform_A": "source",
        "res_B": res_b,
        "platform_B": "follow_up",
        "exceptions": exceptions,
        "time_exec": time_exec
    }
    return exec_metadata


def create_follow(metadata: Dict[str, Any], config: Dict[str, Any]):
    """Change the backend of the passed pyfile."""
    start_metamorph = timer()
    filepath = metadata["py_file_path"]
    file_content = open(filepath, "r").read()

    max_n_transf = config["pipeline"]["max_transformations_per_program"]

    if config["transformation_mode"] == "morphq":
        transf_available = config["morphq_metamorphic_strategies"]
    elif config["transformation_mode"] == "qdiff":
        transf_available = config["qdiff_metamorphic_strategies"]
        # reduce the number of transformations to apply of one, to apply a
        # differential testing transformation at the end of the chain
        # aka a change of backend or optimization level
        max_n_transf = max(1, max_n_transf - 1)
    n_transf_to_apply = \
        random.randint(1, max_n_transf)

    transformation = ChainedTransformation(
        name="Chain",
        metamorphic_strategies_config=transf_available,
        detectors_config=config["detectors"],
        seed=None
    )
    metamorphed_file_content = file_content
    safe_counter = 0
    name_of_transformations_applied = []
    time_of_transformations_applied = []
    while transformation.transf_applied_count < n_transf_to_apply:
        transformation.select_random_transformation()
        start_transformation = timer()
        safe_counter += 1
        if safe_counter > 100:
            if len(name_of_transformations_applied) == 0:
                raise Exception("Could not apply any transformation. " +
                                "Source = Follow.")
            else:
                print("No more available transformations. Stop metamorph.")
                break
        if transformation.check_precondition(metamorphed_file_content):
            metamorphed_file_content = \
                transformation.derive(metamorphed_file_content)
            end_transformation = timer()
            time_transformation = end_transformation - start_transformation
            time_of_transformations_applied.append(time_transformation)
            name_of_transformations_applied.append(
                transformation.get_name_current_transf()
            )
            # remember that by construction the transformations of qdiff
            # are semantically preserving, thus the last transformation to
            # check is always equivalence
            if not transformation.is_semantically_equivalent():
                print(transformation.get_name_current_transf() +
                      " is not semantically equivalent. " +
                      "Thus we stop chain of transformations.")
                break
    print("N. applied transformations: ", transformation.transf_applied_count)

    # append the change of backend or optimization level
    if config["transformation_mode"] == "qdiff":
        diff_testing_transformations = config["qdiff_diff_testing"]
        transformation = ChainedTransformation(
            name="Chain",
            metamorphic_strategies_config=diff_testing_transformations,
            detectors_config=config["detectors"],
            seed=None
        )
        transformation.select_random_transformation()
        if transformation.check_precondition(metamorphed_file_content):
            print("Applying last transformation that serve as " +
                  "the differential testing setup.")
            metamorphed_file_content = \
                transformation.derive(metamorphed_file_content)
            name_of_transformations_applied.append(
                transformation.get_name_current_transf()
            )
        else:
            print("Warning: could not apply diff testing transformation.")

    mr_metadata = transformation.metadata
    transformation = transformation.get_last_applied_transformation()

    experiment_folder = config["experiment_folder"]
    program_id = metadata["program_id"]
    new_filepath = join(
        experiment_folder, "programs", "followup", f"{program_id}.py")
    with open(new_filepath, "w") as f:
        f.write(metamorphed_file_content)

    end_metamorph = timer()
    time_metamorph = end_metamorph - start_metamorph

    new_metadata = {**metadata, }
    new_metadata["py_file_path"] = new_filepath
    new_metadata["metamorphic_info"] = mr_metadata
    new_metadata["metamorphic_transformations"] = \
        name_of_transformations_applied
    new_metadata["time_metamorph"] = time_metamorph
    new_metadata["metamorphic_transformations_times"] = \
        time_of_transformations_applied
    return new_metadata, transformation


def produce_and_test_single_program_couple(config, generator):
    """Fuzz a program and morph it, run both."""
    experiment_folder = config["experiment_folder"]
    if config["track_coverage"]:
        coverage_obj = Coverage(
            data_suffix=False,
            config_file=config["coverage_settings_filepath"])
        coverage_obj.load()
        coverage_obj.start()
        coverage.process_startup()
    program_id, metadata_source = fuzz_source_program(
        generator,
        experiment_folder=experiment_folder,
        config_generation=config["generation_strategy"],
        config=config)
    try:
        metadata_followup, transformation = create_follow(
            metadata_source, config)
    except Exception as e:
        print(f"Program id: {program_id}")
        print(colored(f"Could not create followup. Exception: {e}", 'red'))
        if "Source = Follow" not in str(e):
            traceback.print_exc()
        return
    abs_start_time = time.time()
    current_date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    print(f"Executing: {program_id} ({current_date})")
    exec_metadata = execute_programs(
        metadata_source=metadata_source,
        metadata_followup=metadata_followup)
    # not that if the transformation is a chain of transformations,
    # then we only check the output relationship of the last transformation
    div_metadata = transformation.check_output_relationship(
        result_a=exec_metadata["res_A"],
        result_b=exec_metadata["res_B"])
    all_metadata = dump_all_metadata(
        out_folder=join(experiment_folder, "programs", "metadata"),
        program_id=program_id,
        source=metadata_source, followup=metadata_followup,
        divergence=div_metadata,
        time_exec=exec_metadata["time_exec"],
        abs_start_time=int(abs_start_time),
        exceptions=exec_metadata["exceptions"])
    dump_metadata(
        metadata=exec_metadata,
        metadata_filepath=join(
            experiment_folder, "programs",
            "metadata_exec", f"{program_id}.json"))
    con = get_database_connection(config, "qfl.db")
    # remove metamorphic info because they are not uniform to the
    # table schema for all the relationships
    if "metamorphic_info" in all_metadata["followup"].keys():
        del all_metadata["followup"]["metamorphic_info"]
    if ((exec_metadata["exceptions"]["source"] is not None) or
            (exec_metadata["exceptions"]["followup"] is not None)):
        update_database(con, table_name="CRASHDATA", record=all_metadata)
    else:
        update_database(con, table_name="QFLDATA", record=all_metadata)
        scan_for_divergence(
            config,
            method=config["divergence_threshold_method"],
            test_name=config["divergence_primary_test"],
            alpha_level=config["divergence_alpha_level"])
    if config["track_coverage"]:
        coverage_obj.stop()
        coverage_obj.save()


# LEVEL 2:


def loop(config):
    """Start fuzzing loop."""
    generator = eval(config["generation_strategy"]["generator_object"])()
    budget_time = config["budget_time_per_program_couple"]
    if config["track_coverage"]:
        data_file = join(config["experiment_folder"], "coverage.db")
        print("Data file: ", data_file)
        cov = Coverage(
            data_suffix=False,
            config_file=config["coverage_settings_filepath"])
        between_saves = config["programs_between_coverage_checkpoints_start"]
        between_saves_cap = config["programs_between_coverage_checkpoints_cap"]
    counter_programs = 0
    # for i in range(3):
    while True:
        counter_programs += 1
        if config["track_coverage"] and counter_programs % between_saves == 0:
            filename = str(counter_programs).zfill(10) + ".json"
            print("Saving coverage...")
            elements = os.listdir(config["experiment_folder"])
            files_to_combine = [
                join(config["experiment_folder"], f)
                for f in elements
                if (os.path.isfile(join(config["experiment_folder"], f))
                    and ".coverage" in f)
            ]
            cov.combine(files_to_combine)
            cov.load()
            coverage = cov.json_report(outfile=join(
                config["experiment_folder"], "coverage_reports", filename))
            print(f"Coverage saved! ({coverage:.2f}%) " +
                  f"[programs: {counter_programs}]")
            # we have a variable size of the checkpoint interval at the
            # start to have fine grade info about the coverage
            # increase the time to the next coverage checkpoint
            if between_saves < between_saves_cap:
                between_saves = between_saves * 2
            # if you reach the maximum stop the interval growth
            if between_saves >= between_saves_cap:
                between_saves = between_saves_cap

        if budget_time is not None:
            current_date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            print(f"--------- New programs pair... " +
                  f"[timer: {budget_time} sec] ({current_date}) ----------")
            break_function_with_timeout(
                routine=produce_and_test_single_program_couple,
                seconds_to_wait=budget_time,
                message="Change 'budget_time_per_program_couple'" +
                        " in config yaml file.",
                args=(config, generator)
            )
        else:
            print("New program couple.. [no timer]")
            produce_and_test_single_program_couple(config, generator)


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
        print("Starting loop... [no timer]")
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
