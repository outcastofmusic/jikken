import json
import yaml
import subprocess
import os
from hashlib import md5


def get_code_commit_id(directory=None):
    directory = os.getcwd() if directory is None else directory
    result = subprocess.check_output(["git", "rev-parse", "HEAD"])
    return result.decode()

def load_experiment_from_dir(experiment_dir):
    all_variables = {}
    for root, dirname, filenames in os.walk(experiment_dir):
        for filename in filenames:
            if filename.endswith("json") or filename.endswith("yaml"):
                all_variables[root+filename] = load_experiment_from_file(os.path.join(root, filename))
    return all_variables


def load_experiment_from_file(experiment_filepath):
    if os.path.isdir(experiment_filepath):
        variables = load_experiment_from_dir(experiment_filepath)
    elif experiment_filepath.endswith("yaml") or experiment_filepath.endswith(".json"):
        with open(experiment_filepath, 'rt') as file_handle:
            variables = yaml.load(file_handle)
    else:
        raise IOError("only json and yaml files are supported")
    return variables


def get_schema(dictionary, parameters=False):
    global_definition = ""

    def get_key_schema(dl, definition=None):
        definition = "" if definition is None else definition
        if isinstance(dl, dict):
            for key in sorted(dl.keys()):
                defin = definition + "_" + key if definition != "" else key
                get_key_schema(dl[key], defin)
        elif isinstance(dl, list):
            for item in sorted(dl):
                get_key_schema(item, definition)
        else:
            if parameters:
                final_value = definition + "_" + str(dl)
            else:
                final_value = definition + "_value"
            nonlocal global_definition
            global_definition += final_value + "\n"

    get_key_schema(dictionary)
    return global_definition


def get_hash(input):
    return md5(input.encode()).hexdigest()