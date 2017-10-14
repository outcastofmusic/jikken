import json
import yaml
import subprocess
import os
from hashlib import md5


def get_code_commit_id(directory=None):
    directory = os.getcwd() if directory is None else directory
    result = subprocess.check_output(["git", "rev-parse", "HEAD"])
    return result.decode()


def load_experiment_from_file(experiment_filepath):
    with open(experiment_filepath, 'rt') as file_handle:
        if experiment_filepath.endswith("json"):
            variables = json.load(file_handle)
        elif experiment_filepath.endswith("yaml"):
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