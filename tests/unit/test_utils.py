import json

import jikken.utils as utils
import pytest
import yaml
from git import Repo


@pytest.fixture()
def jikken_configuration_folder(tmpdir):
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


def test_load_from_dir(jikken_configuration_folder):
    conf_dir, expected_variables, json_file, yaml_file = jikken_configuration_folder
    split_dirs_json = json_file.strpath.split("/")
    split_dirs_yaml = yaml_file.strpath.split("/")
    expected_variables = {"_".join(split_dirs_json[-2:]): expected_variables,
                          "_".join(split_dirs_yaml[-3:]): expected_variables
                          }
    variables = utils.load_variables_from_dir(conf_dir.strpath)
    assert variables == expected_variables
    variables = utils.load_variables_from_filepath(conf_dir.strpath)
    assert variables == expected_variables


def test_load_from_file(jikken_configuration_folder):
    _, expected_variables, json_file, yaml_file = jikken_configuration_folder
    variables = utils.load_variables_from_filepath(json_file.strpath)
    assert variables == expected_variables
    variables = utils.load_variables_from_filepath(yaml_file.strpath)
    assert variables == expected_variables


@pytest.fixture()
def setup_git(jikken_configuration_folder):
    conf_dir, expected_variables, json_file, yaml_file = jikken_configuration_folder
    repo = Repo.init(conf_dir.strpath)
    repo.index.add([json_file.strpath, yaml_file.strpath])
    repo.index.commit("initial commit")
    return conf_dir, repo


def test_commit_id_no_git(jikken_configuration_folder):
    conf_dir, expected_variables, json_file, yaml_file = jikken_configuration_folder
    commit_id = utils.get_code_commit_id(conf_dir.strpath)
    assert commit_id is None


def test_commit_id(setup_git):
    conf_dir, repo = setup_git
    commit_id = utils.get_code_commit_id(conf_dir.strpath)
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
