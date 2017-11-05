import copy
import json

import jikken.utils as utils
import os
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
    config_dir = tmpdir.mkdir('experiment').mkdir('config')
    json_file = config_dir.join("experiment.json")
    with json_file.open('w') as f:
        json.dump(expected_variables, f)
    subdir = config_dir.mkdir('subdir')
    yaml_file = subdir.join("experiment.yaml")
    with yaml_file.open('w') as f:
        yaml.dump(expected_variables, f)

    return config_dir, expected_variables, json_file, yaml_file


@pytest.fixture()
def config_directory(config_folder):
    conf_dir, expected_variables, json_file, yaml_file = config_folder
    split_dirs_json = json_file.strpath.split("/")
    split_dirs_yaml = yaml_file.strpath.split("/")
    expected_variables = {"/".join(split_dirs_json[-2:]): expected_variables,
                          "/".join(split_dirs_yaml[-3:]): expected_variables
                          }
    return conf_dir, expected_variables


def test_load_from_dir(config_directory):
    # GIVEN a config directory
    conf_dir, expected_variables = config_directory
    # WHEN I load the directory
    variables = utils.load_variables_from_dir(str(conf_dir))
    # THEN  the variables have been set as a dict with keys the config filepaths
    assert variables == expected_variables
    variables = utils.load_variables_from_filepath(str(conf_dir))
    assert variables == expected_variables


def test_create_dir_from_utils(config_directory):
    """test new directory is given by variables"""
    # GIVEN a a dict of variables  loaded from a config_directory
    conf_dir, expected_variables = config_directory
    new_dir = conf_dir.mkdir("new_dir")
    # WHEN I pass them to create_directory_from_variables
    utils.create_directory_from_variables(str(new_dir), expected_variables)
    # THEN I create a new config dir that mirrors the config_directory
    new_directory = os.path.join(str(new_dir), str(conf_dir).split("/")[-1])
    new_variables = utils.load_variables_from_dir(new_directory)
    assert new_variables == expected_variables


def test_load_from_file(config_folder):
    # Given a config_folder with two files
    config_path, expected_variables, json_file, yaml_file = config_folder
    json_variables = {str(json_file).split("/")[-1]: expected_variables}
    yaml_variables = {str(yaml_file).split("/")[-1]: expected_variables}

    # WHEN I load the json_file
    actual_json_variables = utils.load_variables_from_filepath(json_file.strpath)
    # AND when I load the yaml file
    actual_yaml_variables = utils.load_variables_from_filepath(yaml_file.strpath)
    # THEN the files get loaded in a dict with their filepaths as a key
    assert actual_json_variables == json_variables
    assert actual_yaml_variables == yaml_variables


def test_load_from_wrong_file_raise(config_folder):
    # GIVEN a config_folder with a text file
    config_path, *_ = config_folder
    txt_file = config_path.join("test.txt")
    with txt_file.open('w') as file_handle:
        file_handle.write("this is a test text file")
    # WHEN I try to load the file
    # THEN an IOError is raised
    with pytest.raises(IOError):
        variables = utils.load_variables_from_filepath(str(txt_file))


def test_prepare_variables_no_update(config_directory):
    # GIVEN a config_dir only
    conf_dir, expected_variables = config_directory
    # WHEN I prepare variables
    with utils.prepare_variables(config_directory=str(conf_dir)) as variables_path:
        variables, path = variables_path
        # THEN the path and variables are the config_dir and the variables inside it respectively
        assert path == str(conf_dir)
        assert variables == expected_variables


def test_prepare_variables_with_update_dir(config_directory, tmpdir):
    # GIVEN a conf dir and an update_dir
    conf_dir, expected_variables = config_directory
    updated_variables = {
        "training_parameters":
            {"batch_size": 200,
             },
        "input_parameters":
            {'batch_size': 8,
             }
    }
    update_dir = tmpdir.mkdir("experiment2").mkdir("config")
    json_file = update_dir.join("experiment.json")
    with json_file.open('w') as f:
        json.dump(updated_variables, f)
    # WHEN I pass them to the prepare_variables class
    with utils.prepare_variables(reference_directory=str(conf_dir), config_directory=str(update_dir)) as variables_path:
        variables, path = variables_path
        # THEN a new temporary path is created with new files with the combined updated config files
        assert path != str(conf_dir)
        assert path != str(update_dir)
        assert variables != expected_variables
    expected_variables['config/experiment.json']['training_parameters']['batch_size'] = 200
    expected_variables['config/experiment.json']['input_parameters']['batch_size'] = 8
    assert variables['config/experiment.json'] == expected_variables['config/experiment.json']


def test_prepare_variables_with_update_file(config_folder):
    # GIVEN a conf file and an update_file
    config_path, expected_variables, json_file, yaml_file = config_folder
    expected_variables = {str(json_file).split("/")[-1]: expected_variables}
    updated_variables = {
        "training_parameters":
            {"batch_size": 200,
             },
        "input_parameters":
            {'batch_size': 8,
             }
    }
    root_dir = config_path.parts()[-2]
    update_dir = root_dir.mkdir("config2")
    json_file_2 = update_dir.join("experiment.json")
    with json_file_2.open('w') as f:
        json.dump(updated_variables, f)
    # WHEN I pass them to the prepare_variables class
    with utils.prepare_variables(reference_directory=str(json_file),
                                 config_directory=str(json_file_2)) as variables_path:
        variables, path = variables_path
        # THEN a new temporary path is created with new files with the combined updated config files
        assert variables != expected_variables
    expected_variables['experiment.json']['training_parameters']['batch_size'] = 200
    expected_variables['experiment.json']['input_parameters']['batch_size'] = 8
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


def test_update_variables():
    reference_variables = {
        "testfolder.py": {
            "global_seed": 5,
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
    }

    new_variables = {
        "testfolder.py": {"global_seed": 1,
                          "training_parameters": {
                              "algorithm": "Conv2d"
                          },
                          "input_parameters": {
                              "batch_size": 8
                          }
                          }
    }

    actual_variables = utils.update_variables(reference_dict=reference_variables, update_dict=new_variables)

    expected_variables = {
        "testfolder.py": {"global_seed": 1,
                          "training_parameters":
                              {"batch_size": 100,
                               "algorithm": "Conv2d",
                               "attention": "multiplicative"
                               },
                          "input_parameters":
                              {'batch_size': 8,
                               "filepath": "/data",
                               "preprocessing": True,
                               "transformations": ["stopwords", "tokenize", "remove_punct"]
                               }
                          }
    }

    assert actual_variables == expected_variables
