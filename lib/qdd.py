"""
Quantum Delta Debugging (QDD)

This tool periodically checks if the top divergent circuits are really
reproducibly different or not.

Programming Mantra:
- every function should have 3-5 lines + return statement.
- max one if per function (which gives +3 lines to use).
"""
import click
import os
import sqlite3 as sl
from typing import Dict, List, Tuple, Any
import json
import pandas as pd
from os.path import join
import uuid
import pathlib


from utils import load_config_and_check
from utils import break_function_with_timeout

from utils_db import get_database_connection
from utils_db import update_database
from utils_db import get_program_ids_in_table

from qfl import execute_qasm_program
from qfl import detect_divergence
from qfl import dump_metadata
from qfl import setup_environment
from qfl import estimate_n_samples_needed

from tqdm import tqdm

# LEVEL 3


def get_qasm_metadata(config: Dict[str, Any], program_id: str):
    """Get the metadata for a program."""
    print(f"Reading: {program_id}")
    path_metadata = os.path.join(
        config['experiment_folder'], "programs", "metadata",
        f"{program_id}.json")
    with open(path_metadata, 'r') as f:
        metadata = json.load(f)
    return metadata["qasm"]


def save_rerun_data(
        config: Dict[str, Any],
        con: sl.Connection,
        program_id: str,
        metadata_qasm: Dict[str, Any],
        exec_metadata: Dict[str, Any], div_metadata: Dict[str, Any]):
    """Save the rerun data."""
    rerun_id = uuid.uuid4().hex
    print(f"Saving rerun_id: {rerun_id} (program_id: {program_id})")
    program_folder = join(config["experiment_folder"], "debug", "metadata", program_id)
    pathlib.Path(program_folder).mkdir(parents=True, exist_ok=True)
    all_metadata = {
        "program_id": program_id, "rerun_id": rerun_id,
        "shots": estimate_n_samples_needed(config),
        "qasm": metadata_qasm, "divergence": div_metadata,
    }
    dump_metadata(
        all_metadata,
        join(program_folder, f"{rerun_id}.json"),
        to_indent=True)
    dump_metadata(
        exec_metadata,
        join(program_folder, f"{rerun_id}_exec.json"),
        to_indent=True)
    update_database(con=con, table_name='RERUN', record=all_metadata)


def get_program_ids_in_folder(program_folder: str) -> List[str]:
    """Get all program files."""
    return [f.replace(".json", "") for f in os.listdir(program_folder)
            if f.endswith(".json") and not f.endswith("_exec.json")]


def convert_nested_json_files_to_pandas(list_filepaths: List[str]) -> pd.DataFrame:
    """Create a pandas dataframe with the json file passed."""
    records = []
    for filepaths in tqdm(list_filepaths):
        with open(filepaths, 'r') as in_file:
            data = json.load(in_file)
        records.append(data)
    return pd.json_normalize(records)


# LEVEL 2


def add_new_programs_to_debugging_db(con: sl.Connection, config: Dict[str, Any]):
    """Add new programs to the database."""
    print("Moving new programs to the debugging database.")
    print("This may take a while...")
    present_program_ids = get_program_ids_in_table(con, 'DATA')
    program_folder = join(config["experiment_folder"], "programs", "metadata")
    all_program_ids = get_program_ids_in_folder(program_folder)
    new_program_ids = list(set(all_program_ids) - set(present_program_ids))
    new_filenames = [join(program_folder, f"{program_id}.json")
                     for program_id in new_program_ids]
    df_to_add = convert_nested_json_files_to_pandas(new_filenames)
    available_columns = df_to_add.columns
    detector_columns = [c for c in available_columns if c.startswith("divergence.")]
    qasm_columns = [c for c in available_columns if c.startswith("qasm.")]
    columns_to_save = ['program_id', 'shots'] + qasm_columns + detector_columns
    df_to_add[columns_to_save].to_sql('DATA', con, if_exists='append')


def pick_k_most_divergent_program_ids_with_no_rerun(
        con: sl.Connection, test_name: str = 'ks', top_k: int = 3):
    """Pick the most divergent program."""
    programs_already_debugged = get_program_ids_in_table(con, table_name="RERUN")
    if len(programs_already_debugged) == 0:
        clause_to_exclude_already_debugged_programs = ""
    else:
        clause_to_exclude_already_debugged_programs = """
        WHERE program_id NOT IN (SELECT DISTINCT program_id FROM RERUN)
        """
    df_most_divergent = pd.read_sql(f'''
        SELECT program_id, [divergence.{test_name}.statistic], [divergence.{test_name}.p-value]
        FROM DATA
        {clause_to_exclude_already_debugged_programs}
        ORDER BY
            [divergence.{test_name}.statistic] DESC,
            [divergence.{test_name}.p-value]  ASC
        LIMIT {top_k};
    ''', con)
    return list(df_most_divergent["program_id"])


def debug_loop(
        program_id: str,
        config: Dict[str, Any],
        max_runs_per_suspect_bug: int = 10):
    """Debug a single divergent case."""
    con = get_database_connection(config)
    metadata_qasm = get_qasm_metadata(config, program_id)
    for i in range(max_runs_per_suspect_bug):
        print(f"Execution iteration {i}", end=" - ")
        exec_metadata = execute_qasm_program(
            config, program_id, metadata_qasm)
        div_metadata = detect_divergence(exec_metadata, detectors=config["detectors"])
        save_rerun_data(
            config, con, program_id=program_id,
            metadata_qasm=metadata_qasm,
            exec_metadata=exec_metadata, div_metadata=div_metadata)
    con.close()

# LEVEL 1


def timed_debug_loop(
        program_id: str,
        config: Dict[str, Any],
        max_runs_per_suspect_bug: int = 10,
        max_seconds_per_suspect_bug: int = 120):
    """Continually apply the QDD algorithm in loop."""
    if max_seconds_per_suspect_bug is not None:
        break_function_with_timeout(
            routine=debug_loop,
            seconds_to_wait=max_seconds_per_suspect_bug,
            message="Change 'max_seconds_per_suspect_bug' in config yaml file.",
            args=(program_id, config, max_runs_per_suspect_bug)
        )
    else:
        debug_loop(config)


def start_qdd_loop(
        config: Dict[str, Any],
        max_runs_per_suspect_bug: int = 10,
        max_seconds_per_suspect_bug: int = 120,
        update_db_every_n_programs: int = 100,
        primary_detector_for_debug: str = 'ks'):
    """Scan the loop for divergent cases."""
    while True:
        con = get_database_connection(config)
        add_new_programs_to_debugging_db(con, config)
        divergent_ids = pick_k_most_divergent_program_ids_with_no_rerun(
            con=con, test_name=primary_detector_for_debug, top_k=update_db_every_n_programs)
        con.close()
        for program_id in divergent_ids:
            timed_debug_loop(
                program_id, config,
                max_runs_per_suspect_bug, max_seconds_per_suspect_bug)


def setup_debugging_database(config: Dict[str, Any]):
    """Setup the database."""
    db_path = os.path.join(config['experiment_folder'], "qdd_debugging.db")
    con = sl.connect(db_path)
    add_new_programs_to_debugging_db(con, config)
    con.close()


# LEVEL 0:


@click.command()
@click.argument('config_file')
def qdd(config_file):
    """Run QDD."""
    config = load_config_and_check(config_file)
    setup_debugging_database(config)
    setup_environment(
        experiment_folder=config["experiment_folder"],
        folder_structure=config["folder_structure"])
    start_qdd_loop(
        config,
        max_runs_per_suspect_bug=config['max_runs_per_suspect_bug'],
        max_seconds_per_suspect_bug=config['max_seconds_per_suspect_bug'],
        update_db_every_n_programs=config['update_db_every_n_programs'],
        primary_detector_for_debug=config["primary_detector_for_debug"]
    )


if __name__ == '__main__':
    qdd()