import pytest
from jikken.api import run_experiment
from jsonpickle import json


def test_run_experiment_given_script_and_config(file_setup, capsys):
    conf_path, script_path, config_json = file_setup
    run_experiment(configuration_path=conf_path, script_path=script_path)
    out, err = capsys.readouterr()
    expected_output = json.dumps(config_json)
    assert out[2:-4] == expected_output
