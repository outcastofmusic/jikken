import ast
import copy
import json
import os
from hashlib import md5
from tempfile import TemporaryDirectory

import yaml
from git import InvalidGitRepositoryError, Repo
from contextlib import contextmanager


@contextmanager
def prepare_variables(*, config_directory, reference_directory=None):
    """create a new updated config given a reference_dire and a config_dir"""
    if reference_directory is None:
        variables = load_variables_from_filepath(config_directory)
        config_dir = config_directory
    else:
        reference_variables = load_variables_from_filepath(reference_directory)
        updated_variables = load_variables_from_filepath(config_directory)
        variables = update_variables(reference_variables, updated_variables)
        new_dir = TemporaryDirectory()
        create_directory_from_variables(new_dir.name, variables)
        if os.path.isfile(config_directory):
            config_dir = os.path.join(new_dir.name, list(variables.keys())[0])
        else:
            config_dir = new_dir.name
    yield variables, config_dir

    if reference_directory is not None:
        new_dir.cleanup()


def get_repo_origin(directory):
    """Get the url of the git origin of a repo """
    url = None
    try:
        repo = Repo(directory)
        if len(repo.remotes) > 0:
            url = repo.remotes[0].url
    except InvalidGitRepositoryError:
        url = None
    return url


def get_commit_status(directory):
    """Get the commit status of a repo (dirty or not)"""
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
    """Load variables dict from a directory path"""
    all_variables = {}
    root_path = os.path.dirname(experiment_dir)
    for root, dirname, filenames in os.walk(experiment_dir):
        for filename in filenames:
            if filename.endswith("json") or filename.endswith("yaml"):
                root_key = "/".join(root[len(root_path) + 1:].split("/"))
                key = filename if root_key == "" else root_key + "/" + filename
                all_variables[key] = load_variables_from_filepath(os.path.join(root, filename), root=False)
    return all_variables


def load_variables_from_filepath(experiment_filepath, root=True):
    """Load variables dict from a config path (directory or file)"""
    if os.path.isdir(experiment_filepath):
        variables = load_variables_from_dir(experiment_filepath)
    elif experiment_filepath.endswith("yaml") or experiment_filepath.endswith("json"):
        with open(experiment_filepath, 'rt') as file_handle:
            values = yaml.load(file_handle)
        variables = {str(experiment_filepath).split("/")[-1]: values} if root else values

    else:
        raise IOError("only json and yaml files are supported")
    return variables


def get_schema(dictionary, parameters=False, delimiter="_"):
    """Get a schema of the config of the dictionary"""
    global_definition = ""

    def get_key_schema(dl, definition=None):
        definition = "" if definition is None else definition
        if isinstance(dl, dict):
            for key in sorted(dl.keys()):
                defin = definition + delimiter + key if definition != "" else key
                get_key_schema(dl[key], defin)
        elif isinstance(dl, list):
            for item in sorted(dl):
                get_key_schema(item, definition)
        else:
            if parameters:
                final_value = definition + delimiter + str(dl)
            else:
                final_value = definition + delimiter + "value"
            nonlocal global_definition
            global_definition += final_value + "\n"

    get_key_schema(dictionary)
    return global_definition


def get_hash(input_string: (str, int)):
    """ Return the md5 has of the input

    Args:
        input_string (str, int): A string that will be hash

    Returns:
        str: The md5 hash

    """
    input_string = str(input_string)
    return md5(input_string.encode()).hexdigest()


def update_variables(reference_dict, update_dict):
    """Update variables in a reference dict from an update dict"""
    new_dict = copy.copy(reference_dict)
    update_schema = get_schema(update_dict, parameters=True, delimiter="\t")
    for row in update_schema.split("\n")[:-1]:
        keys = row.split("\t")
        ref = new_dict
        for key in keys[:-2]:
            ref = ref[key]
        try:
            literal_value = ast.literal_eval(keys[-1])
        except ValueError:
            literal_value = keys[-1]
        except SyntaxError:
            literal_value = keys[-1]
        ref[keys[-2]] = literal_value
    return new_dict


def create_directory_from_variables(root_dir, variables):
    """Create a new config dir from a variables dict"""
    for key in variables.keys():
        key_dir = os.path.join(root_dir, key)
        os.makedirs(os.path.dirname(key_dir), exist_ok=True)

        if key_dir.endswith(".json"):
            with open(key_dir, 'wt') as file_handle:
                json.dump(variables[key], file_handle)
        elif key_dir.endswith(".yaml"):
            with open(key_dir, 'wt') as file_handle:
                yaml.dump(variables[key], file_handle)


def prepare_command(configuration_path, setup):
    """Prepare a cmd command to run  a script"""
    # TODO think of a way to enable more generic inputs to scripts
    # in the arguments we add the input path and the output path as positional arguments

    extra_kwargs = [x for argument in setup.args for x in argument]
    input_path = getattr(setup, "input_path", None)
    output_path = getattr(setup, "output_path", None)
    if output_path is not None:
        extra_kwargs = ["-o", output_path] + extra_kwargs
    if input_path is not None:
        extra_kwargs = ["-i", input_path] + extra_kwargs
    if setup.script_path.endswith(".py"):
        cmd = ["python3", setup.script_path, configuration_path] + extra_kwargs
    elif setup.script_path.endswith(".sh"):
        cmd = ["bash", setup.script_path, configuration_path] + extra_kwargs
    return cmd


def check_mongo(uri=None):
    """Check if mongo db is available in the uri provided"""
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError
    uri = "mongodb://localhost:27019" if uri is None else uri
    client = MongoClient(uri, serverSelectionTimeoutMS=300)
    try:
        client.server_info()
        found_database = True
    except ServerSelectionTimeoutError:
        found_database = False
    return found_database


def check_es(url=None):
    from elasticsearch import Elasticsearch
    url = "http://localhost:9200" if url is not None else url
    es = Elasticsearch(url)
    try:
        es.cluster.health()
        found_database = True
    except ConnectionError:
        found_database = False

    return found_database


def get_resume_name(stage_name):
    """return a new name with resume and an increasing index"""
    split_stage_name = stage_name.split("_")
    if len(split_stage_name) > 2 and split_stage_name[-2] == "resume":
        resume_index = int(split_stage_name[-1]) + 1
        return "_".join(split_stage_name[:-2] + ["resume_{}".format(resume_index)])
    else:
        return stage_name + "_resume_0"
