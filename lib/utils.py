import os
import json
import yaml
from typing import List


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
