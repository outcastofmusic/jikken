import os
import re
import pytest

import json
from contextlib import contextmanager

import jikken
from jikken.api import run_multistage
from jikken.setups import MultiStageExperimentSetup
from jikken.multistage import STAGE_METADATA


def setup_database_stub(db):
    @contextmanager
    def db_stub():
            yield db

    return db_stub()

def test_run_multistage_given_script_and_config(tmpdir, file_setup, capsys, jikken_db, mocker):
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    conf_path, script_path, config_json = file_setup

    stage_one_output_path = tmpdir.mkdir("stage_one_output")
    stage_two_output_path = tmpdir.mkdir("stage_two_output")
    setup = MultiStageExperimentSetup(
        name="multistage_test",
        configuration_path=conf_path,
        script_path=script_path,
        input_path=None,
        output_path=str(stage_one_output_path),
        stage_name="stage_one"
    )
    run_multistage(setup=setup)
    out, err = capsys.readouterr()
    expected_output = json.dumps(config_json)
    assert os.path.exists(os.path.join(str(stage_one_output_path), STAGE_METADATA))
    assert out[2:246] == expected_output
    assert out[-17:] == '\nExperiment Done\n'

def test_run_multistage_given_script_and_config(tmpdir, file_setup, capsys, jikken_db, mocker):
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    conf_path, script_path, config_json = file_setup

    stage_one_output_path = tmpdir.mkdir("stage_one_output")
    stage_two_output_path = tmpdir.mkdir("stage_two_output")
    stage_three_output_path = tmpdir.mkdir("stage_three_output")
    setup = MultiStageExperimentSetup(
    name="multistage_test",
    configuration_path=conf_path,
    script_path=script_path,
    output_path=str(stage_one_output_path),
    stage_name="stage_one"
    )
    run_multistage(setup=setup)
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))

    setup = MultiStageExperimentSetup(
        name="multistage_test",
        configuration_path=conf_path,
        script_path=script_path,
        input_path=str(stage_one_output_path),
        output_path=str(stage_two_output_path),
        stage_name="stage_two"
    )
    run_multistage(setup=setup)
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    setup = MultiStageExperimentSetup(
        name="multistage_test",
        configuration_path=conf_path,
        script_path=script_path,
        input_path=str(stage_two_output_path),
        output_path=str(stage_three_output_path),
        stage_name="stage_three"
    )
    run_multistage(setup=setup)
    out, err = capsys.readouterr()
    assert os.path.exists(os.path.join(str(stage_one_output_path), STAGE_METADATA))
    assert os.path.exists(os.path.join(str(stage_two_output_path), STAGE_METADATA))
    assert os.path.exists(os.path.join(str(stage_three_output_path), STAGE_METADATA))
    pattern = re.compile("\nExperiment Done\n")
    results = re.findall(pattern, out)
    assert len(results) == 3
    assert out[-17:] == '\nExperiment Done\n'
