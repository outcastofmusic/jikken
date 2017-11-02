import json
from jikken.api import run


def test_run_experiment_given_script_and_config(file_setup, capsys):
    conf_path, script_path, config_json = file_setup
    run(configuration_path=conf_path, script_path=script_path)
    out, err = capsys.readouterr()
    expected_output = json.dumps(config_json)
    assert out[2:-4] == expected_output


def test_run_experiment_with_tags(file_setup, capsys):
    conf_path, script_path, config_json = file_setup
    tags = ["test", 'hi']
    run(configuration_path=conf_path, script_path=script_path, tags=tags)
    out, err = capsys.readouterr()
    expected_output = json.dumps(config_json)
    assert out[2:-4] == expected_output


def test_run_experiment_with_extra_args(file_setup, capsys):
    conf_path, script_path, config_json = file_setup
    extra_args = ["--var1=1", "--var2=false"]
    run(configuration_path=conf_path, script_path=script_path, args=extra_args)
    out, err = capsys.readouterr()
    expected_output = json.dumps(config_json)
    assert out[2:-26] == expected_output
    assert out[-22:-15] == "var1= 1"
    assert out[-13:-2] == "var2= false"
