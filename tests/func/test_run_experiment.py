import json
from contextlib import contextmanager

import jikken
from jikken.api import run, ExperimentSetup


def setup_database_stub(db):
    @contextmanager
    def db_stub():
        yield db
    return db_stub()


def test_run_experiment_given_script_and_config(file_setup, capsys, jikken_db, mocker):
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    conf_path, script_path, config_json = file_setup
    setup = ExperimentSetup(name="test",configuration_path=conf_path, script_path=script_path)
    run(setup=setup)
    out, err = capsys.readouterr()
    expected_output = json.dumps(config_json)
    assert out[2:246] == expected_output
    assert out[-17:] == '\nExperiment Done\n'


def test_run_experiment_with_tags(file_setup, capsys, jikken_db, mocker):
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    conf_path, script_path, config_json = file_setup
    tags = ["test", 'hi']
    setup = ExperimentSetup(name="test",configuration_path=conf_path, script_path=script_path, tags=tags)
    run(setup=setup)
    out, err = capsys.readouterr()
    expected_output = json.dumps(config_json)
    assert out[2:246] == expected_output
    assert out[-17:] == '\nExperiment Done\n'


def test_run_experiment_with_extra_args(file_setup, capsys, jikken_db, mocker):
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    conf_path, script_path, config_json = file_setup
    extra_args = ["--var1=1", "--var2=false"]
    setup = ExperimentSetup(name="test",configuration_path=conf_path, script_path=script_path, args=extra_args)
    run(setup=setup)
    out, err = capsys.readouterr()
    expected_output = json.dumps(config_json)
    assert out[2:246] == expected_output
    assert out[-38:-31] == "var1= 1"
    assert out[-29:-18] == "var2= false"
    assert out[-17:] == '\nExperiment Done\n'


def test_run_experiment_with_error(file_setup, capsys, jikken_db, mocker):
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    conf_path, script_path, config_json = file_setup
    extra_args = ["--error=True"]
    setup = ExperimentSetup(name="test",configuration_path=conf_path, script_path=script_path, args=extra_args)
    run(setup=setup)
    out, err = capsys.readouterr()
    assert out[-19:] == '\nExperiment Failed\n'


def test_run_experiment_and_experiment_is_added_to_database(file_setup, jikken_db, capsys, mocker):
    # GIVEN a conf_path and a script_path
    conf_path, script_path, config_json = file_setup
    tags = ["test", 'hi']
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    # WHEN I run an experiment
    setup = ExperimentSetup(name="test",configuration_path=conf_path, script_path=script_path, tags=tags)
    run(setup=setup)
    # THEN the experiment gets added to the database
    assert jikken_db.count() == 1
    # And the stdout should have added the captured expected_output
    expected_output = json.dumps(config_json)
    exp = jikken_db.list_experiments()[0]
    assert exp['stdout'][2:-3] == expected_output
