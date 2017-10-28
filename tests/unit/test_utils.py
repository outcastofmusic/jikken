import json

import jikken.utils as utils
import pytest
import yaml


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
    json_file.write(json.dumps(expected_variables))
    subdir = tmpdir.mkdir('subdir')
    yaml_file = subdir.join("experiment.yaml")
    yaml_file.write(yaml.dump(expected_variables))

    return tmpdir.strpath, expected_variables, json_file, yaml_file


def test_load_from_dir(jikken_configuration_folder):
    conf_dir, expected_variables, json_file, yaml_file = jikken_configuration_folder
    split_dirs_json = json_file.strpath.split("/")
    split_dirs_yaml = yaml_file.strpath.split("/")
    expected_variables = {"_".join(split_dirs_json[-2:]): expected_variables,
                          "_".join(split_dirs_yaml[-3:]): expected_variables
                          }
    variables = utils.load_variables_from_dir(conf_dir)
    assert variables == expected_variables
    variables = utils.load_variables_from_filepath(conf_dir)
    assert variables == expected_variables


def test_load_from_file(jikken_configuration_folder):
    conf_dir, expected_variables, json_file, yaml_file = jikken_configuration_folder
    variables = utils.load_variables_from_filepath(json_file.strpath)
    assert variables == expected_variables
    variables = utils.load_variables_from_filepath(yaml_file.strpath)
    assert variables == expected_variables
