import os
import json
import yaml
from typing import List
import subprocess
from itertools import combinations
from functools import reduce
import pandas as pd

from json.decoder import JSONDecodeError


def load_config_and_check(config_file: str, required_keys: List[str] = []):
    """Load the config file and check that it has the right keys."""
    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    for key in required_keys:
        assert key in config.keys(), f"Missing key: {key}"
    return config


def load_json(filename, folder):
    """
    Read the json file at the given path.
    """
    with open(os.path.join(folder, filename), 'r') as f:
        return json.load(f)


def load_multiple_json(program_id, folder):
    """Read all the json files refering to a specific program.

    Note that we assume that the files are named in the following way:
    <program_id>_<execution_number>.json
    """
    filepath_executions = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.startswith(f"{program_id}_") and f.endswith('.json')
    ]
    return read_multiple_execution_as_one(filepath_executions)


def join_two_executions(exec_a, exec_b):
    return {
        k: exec_a.get(k, 0) + exec_b.get(k, 0)
        for k in set(exec_a) | set(exec_b)
    }


def read_multiple_execution_as_one(filepath_executions):
    """
    Join all the dictionary result in one.

    x = {'both1': 1, 'both2': 2, 'only_x': 100}
    y = {'both1': 10, 'both2': 20, 'only_y': 200}

    print {k: x.get(k, 0) + y.get(k, 0) for k in set(x)}
    print {k: x.get(k, 0) + y.get(k, 0) for k in set(x) & set(y)}
    print {k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)}

    Results:

        {'both2': 22, 'only_x': 100, 'both1': 11}
        {'both2': 22, 'both1': 11}
        {'only_y': 200, 'both2': 22, 'both1': 11, 'only_x': 100}
    """
    all_dicts = [
        load_json(
            filename=os.path.basename(filepath),
            folder=os.path.dirname(filepath))
        for filepath in filepath_executions
    ]
    return reduce(join_two_executions, all_dicts)



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


def iterate_parallel_n(folders, filetype, parse_json=False):
    """
    Iterate over the files in the given folders.

    Note that only files in common between the folders are yielded.
    """
    files_in_folders = [
        os.listdir(folder) for folder in folders
    ]

    files_in_common = list(set.intersection(*map(set, files_in_folders)))
    files_to_yield = list(sorted([
        file for file in files_in_common
        if file.endswith(filetype)]))

    for filename in files_to_yield:
        filename_without_extension = filename.replace(filetype, "")
        result_tuple = []
        result_tuple.append(filename_without_extension)
        for folder in folders:
            # open the file and yield it
            with open(os.path.join(folder, filename), 'r') as f:
                if parse_json and filetype == '.json':
                    # read json file
                    file_content = json.load(f)
                else:
                    # read any other file
                    file_content = f.read()
                f.close()
                result_tuple.append(file_content)
            yield result_tuple


# COMBINATIONS OF COMPARISONS

def read_execution_folder(folder_with_execs, compiler_name):
    """Parse execution folder: info on the program_id and execution."""
    files = os.listdir(os.path.join(folder_with_execs, compiler_name))
    records = []
    for filename in files:
        new_record = {}
        new_record["compiler_name"] = compiler_name
        new_record["program_id"] = filename.split("_")[0]
        new_record["exec_iteration"] = \
            filename.split("_")[1].replace(".json", "")
        new_record["filename"] = filename
        new_record["filepath"] = os.path.join(
            folder_with_execs, compiler_name, filename)
        records.append(new_record)
    return records


def iterate_over_program_ids(execution_folder, compilers_names):
    """Iterate over all possible program_IDs.

    It yields the group with all pairs of executions refering to the same
    program_ID.
    """
    all_records = []
    for i_compiler in compilers_names:
        i_records = read_execution_folder(
            folder_with_execs=execution_folder,
            compiler_name=i_compiler)
        all_records.extend(i_records)

    df_all = pd.DataFrame.from_records(all_records)

    df_all_pairs = create_pairs(
        df_all_executions=df_all,
        compilers_names=compilers_names)

    for program_id in sorted(df_all_pairs["program_id"].unique()):
        print(f"program_id: {program_id}")
        # keep only pairs of this program ID
        df_single_program_id = df_all_pairs[
            df_all_pairs["program_id"] == program_id
        ]
        # prepare the pairs of paths to the two execution results
        # from two different platforms
        pairs_single_program_id = list(zip(
            df_single_program_id["filepath_x"],
            df_single_program_id["filepath_y"]
        ))
        yield program_id, pairs_single_program_id


def create_pairs(df_all_executions, compilers_names):
    """Create all comparisons of executions from different platforms."""
    df = df_all_executions
    # get all possible pairs of platforms
    platforms_pairs = combinations(compilers_names, 2)

    df_pairs_all_platforms = []

    for platfrom_a, platfrom_b in platforms_pairs:
        df_a = df[df["compiler_name"] == platfrom_a]
        df_b = df[df["compiler_name"] == platfrom_b]
        df_a_b = pd.merge(df_a, df_b, on="program_id")
        df_pairs_all_platforms.append(df_a_b)

    df_all_pairs = pd.concat(df_pairs_all_platforms, axis= 1)
    return df_all_pairs


def iterate_over_pairs_of_group(pairs):
    """It iterates over the group made of pairs of json.

    It yields every time two dictionary representing the execution of the two
    elements in a pair.
    """
    for path_exec_a, path_exec_b in pairs:
        with open(path_exec_a, 'r') as f:
            res_a = json.load(f)
        with open(path_exec_b, 'r') as f:
            res_b = json.load(f)
        yield path_exec_a, path_exec_b, res_a, res_b


# QUANTUM CONVERSION


def convert(source_folder, dest_folder, dest_format="pyquil", qconvert_path=None):
    if qconvert_path is None:
        raise ValueError("qconvert_path must be specified")
    try:
        files = sorted(os.listdir(source_folder), key=lambda e: int(e.split("_")[0]))
    except ValueError:
        files = sorted(os.listdir(source_folder), key=lambda e: int(e.split(".")[0]))
    qasm_files = [f for f in files if f.endswith(".qasm")]
    print(qasm_files)
    for filename in qasm_files:
        src_filepath = os.path.join(source_folder, filename)
        dest_filepath = os.path.join(dest_folder, filename.replace(".qasm", "_" + dest_format) + ".py")
        string_to_execute = f"{qconvert_path} -h -s qasm -d {dest_format} -i {src_filepath} -o {dest_filepath}"
        print(string_to_execute)
        os.system(string_to_execute)


def run_programs(source_folder, dest_folder, python_path=None, n_executions=1):
    if python_path is None:
        raise ValueError("python_path must be specified")
    try:
        files = sorted(os.listdir(source_folder), key=lambda e: int(e.split("_")[0]))
    except ValueError:
        files = sorted(os.listdir(source_folder), key=lambda e: int(e.split(".")[0]))
    py_files = [f for f in files if f.endswith(".py")]
    for filename in py_files:
        prefix = filename.split("_")[0]
        print(f"Executing: {filename}")
        for exec_iter in range(n_executions):
            out_file_path = os.path.join(dest_folder, f"{prefix}_{exec_iter}.json")
            print(f"Saving: {out_file_path}")
            with open(out_file_path, 'w') as output_file:
                script_to_execute = os.path.join(source_folder, filename)
                proc = subprocess.Popen(
                    [python_path, script_to_execute],
                    stdout=subprocess.PIPE)
                output = str(proc.stdout.read().decode('unicode_escape'))
                output = output.replace("'", '"')
                try:
                    res = json.loads(output)
                except JSONDecodeError as e:
                    print("Execution Error:", e)
                    res = {"0000000000000000": 8192}
                # print(res)
                json.dump(res, output_file)


def convert_single_program(target_program, dest_folder, dest_format="pyquil", qconvert_path=None):
    if qconvert_path is None:
        raise ValueError("qconvert_path must be specified")
    filename = os.path.basename(target_program)
    dest_filepath = os.path.join(dest_folder, filename.replace(".qasm", ".py"))
    string_to_execute = f"{qconvert_path} -h -s qasm -d {dest_format} -i {target_program} -o {dest_filepath}"
    # print(string_to_execute)
    os.system(string_to_execute)
    return dest_filepath


def run_single_program(target_file, dest_folder, python_path=None):
    if python_path is None:
        raise ValueError("python_path must be specified")
    filename = os.path.basename(target_file).replace(".py", "")
    with open(os.path.join(dest_folder, filename + ".json"), 'w') as output_file:
        proc = subprocess.Popen(
            [python_path, target_file],
            stdout=subprocess.PIPE)
        output = str(proc.stdout.read().decode('unicode_escape'))
        output = output.replace("'", '"')
        res = json.loads(output)
        #print(res)
        json.dump(res, output_file)
    return res