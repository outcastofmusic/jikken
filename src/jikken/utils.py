import os
from hashlib import md5

import yaml
from git import InvalidGitRepositoryError, Repo


def get_repo_origin(directory):
    url = None
    try:
        repo = Repo(directory)
        if len(repo.remotes) > 0:
            url = repo.remotes[0].url
    except InvalidGitRepositoryError:
        url = None
    return url


def get_commit_status(directory):
    status = None
    try:
        repo = Repo(directory)
        status = repo.is_dirty()
    except InvalidGitRepositoryError:
        status = None
    return status


def get_commit_id(directory):
    """Returns the current commit_id of the git folder or None if the directory is not a git repo

    Args:
        directory (str): The git directory of the code

    Returns:
            (str): the commit_id
    """
    try:
        repo = Repo(directory)
        commit_id = repo.commit().hexsha
    except InvalidGitRepositoryError:
        commit_id = None
    return commit_id


def load_variables_from_dir(experiment_dir):
    all_variables = {}
    root_path = os.path.dirname(experiment_dir)
    for root, dirname, filenames in os.walk(experiment_dir):
        for filename in filenames:
            if filename.endswith("json") or filename.endswith("yaml"):
                root_key = "_".join(root[len(root_path) + 1:].split("/"))
                key = filename if root_key == "" else root_key + "_" + filename
                all_variables[key] = load_variables_from_filepath(os.path.join(root, filename))
    return all_variables


def load_variables_from_filepath(experiment_filepath):
    if os.path.isdir(experiment_filepath):
        variables = load_variables_from_dir(experiment_filepath)
    elif experiment_filepath.endswith("yaml") or experiment_filepath.endswith("json"):
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


def get_hash(input_string: str):
    """ Return the md5 has of the input

    Args:
        input_string (str): A string that will be hash

    Returns:
        str: The md5 hash

    """
    return md5(input_string.encode()).hexdigest()
