import json

import jikken.utils as utils
import pytest
import yaml
from git import Repo


@pytest.fixture()
def config_folder(tmpdir):
    expected_variables = {
        "training_parameters":
            {"batch_size": 100,
             "algorithm": "Seq2Seq",
             "attention": "multiplicative"
             },
        "input_parameters":
            {'batch_size': 4,
             "filepath": "/data",
             "preprocessing": True,
             "transformations": ["stopwords", "tokenize", "remove_punct"]
             }

    }
    json_file = tmpdir.join("experiment.json")
    with json_file.open('w') as f:
        json.dump(expected_variables, f)
    subdir = tmpdir.mkdir('subdir')
    yaml_file = subdir.join("experiment.yaml")
    with yaml_file.open('w') as f:
        yaml.dump(expected_variables, f)

    return tmpdir, expected_variables, json_file, yaml_file


def test_load_from_dir(config_folder):
    conf_dir, expected_variables, json_file, yaml_file = config_folder
    split_dirs_json = json_file.strpath.split("/")
    split_dirs_yaml = yaml_file.strpath.split("/")
    expected_variables = {"_".join(split_dirs_json[-2:]): expected_variables,
                          "_".join(split_dirs_yaml[-3:]): expected_variables
                          }
    variables = utils.load_variables_from_dir(conf_dir.strpath)
    assert variables == expected_variables
    variables = utils.load_variables_from_filepath(conf_dir.strpath)
    assert variables == expected_variables


def test_load_from_file(config_folder):
    _, expected_variables, json_file, yaml_file = config_folder
    variables = utils.load_variables_from_filepath(json_file.strpath)
    assert variables == expected_variables
    variables = utils.load_variables_from_filepath(yaml_file.strpath)
    assert variables == expected_variables


@pytest.fixture()
def setup_git(config_folder):
    conf_dir, expected_variables, json_file, yaml_file = config_folder
    repo = Repo.init(conf_dir.strpath)
    repo.index.add([json_file.strpath, yaml_file.strpath])
    repo.index.commit("initial commit")
    return conf_dir, repo


def test_commit_id_no_repo(config_folder):
    conf_dir, expected_variables, json_file, yaml_file = config_folder
    commit_id = utils.get_commit_id(conf_dir.strpath)
    assert commit_id is None


def test_commit_dirt_no_repo(config_folder):
    conf_dir, expected_variables, json_file, yaml_file = config_folder
    commit_status = utils.get_commit_status(conf_dir.strpath)
    assert commit_status is None


def test_commit_dirty(setup_git):
    conf_dir, repo = setup_git
    commit_dirty = utils.get_commit_status(conf_dir.strpath)
    assert commit_dirty == False
    newfile = conf_dir.join("new_file.json")
    with newfile.open('w') as f:
        yaml.dump({'data': 1}, f)
    repo.index.add([newfile.strpath])
    commit_dirty = utils.get_commit_status(conf_dir.strpath)
    assert commit_dirty == True


def test_commit_id(setup_git):
    conf_dir, repo = setup_git
    commit_id = utils.get_commit_id(conf_dir.strpath)
    expected_commit_id = repo.commit().hexsha
    assert expected_commit_id == commit_id


def test_repo_no_origin(setup_git):
    conf_dir, repo = setup_git
    origin = utils.get_repo_origin(conf_dir.strpath)
    assert origin is None


def test_repo_origin(setup_git):
    conf_dir, repo = setup_git
    repo.create_remote(name='origin', url='dummy_url')
    origin = utils.get_repo_origin(conf_dir.strpath)
    expected_url = repo.remotes.origin.url
    assert expected_url == origin

expected_schema = \
"""input_parameters_batch_size_value
input_parameters_filepath_value
input_parameters_preprocessing_value
input_parameters_transformations_value
input_parameters_transformations_value
input_parameters_transformations_value
training_parameters_algorithm_value
training_parameters_attention_value
training_parameters_batch_size_value
"""

def test_get_schema(config_folder):
    conf_dir, expected_variables, json_file, yaml_file = config_folder
    schema = utils.get_schema(expected_variables)
    assert schema == expected_schema


expected_schema_parameters = \
"""input_parameters_batch_size_4
input_parameters_filepath_/data
input_parameters_preprocessing_True
input_parameters_transformations_remove_punct
input_parameters_transformations_stopwords
input_parameters_transformations_tokenize
training_parameters_algorithm_Seq2Seq
training_parameters_attention_multiplicative
training_parameters_batch_size_100
"""
def test_get_schema_parameters(config_folder):
    conf_dir, expected_variables, json_file, yaml_file = config_folder
    schema = utils.get_schema(expected_variables, parameters=True)
    assert schema == expected_schema_parameters
