import os
import json
import yaml
from typing import List
import subprocess


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


# QUANTUM CONVERSION


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


def convert_single_program(target_program, dest_folder, dest_format="pyquil", qconvert_path=None):
    if qconvert_path is None:
        raise ValueError("qconvert_path must be specified")
    filename = os.path.basename(target_program)
    dest_filepath = os.path.join(dest_folder, filename.replace(".qasm", "_" + dest_format) + ".py")
    string_to_execute = f"{qconvert_path} -h -s qasm -d {dest_format} -i {target_program} -o {dest_filepath}"
    #print(string_to_execute)
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