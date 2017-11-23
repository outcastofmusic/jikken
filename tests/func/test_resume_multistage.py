import os
import re
import pytest

import json
from contextlib import contextmanager

import jikken
from jikken.api import run_stage, resume_stage
from jikken.setups import MultiStageExperimentSetup
from jikken.multistage import STAGE_METADATA


def setup_database_stub(db):
    @contextmanager
    def db_stub():
        yield db

    return db_stub()


def test_resume_multistage_given_script_and_config(tmpdir, file_setup, capsys, jikken_db, mocker):
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    conf_path, script_path, config_json = file_setup

    stage_one_output_path = tmpdir.mkdir("stage_one_output")
    setup = MultiStageExperimentSetup(
        name="multistage_test",
        configuration_path=conf_path,
        script_path=script_path,
        input_path=None,
        output_path=str(stage_one_output_path),
        stage_name="stage_one"
    )
    run_stage(setup=setup)
    assert os.path.exists(os.path.join(str(stage_one_output_path), STAGE_METADATA))
    metadata = json.load(open(os.path.join(str(stage_one_output_path), STAGE_METADATA)))
    setup2 = MultiStageExperimentSetup(
        name="multistage_test",
        configuration_path=conf_path,
        script_path=script_path,
        input_path=None,
        output_path=str(stage_one_output_path),
        stage_name="stage_one"
    )
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    resume_stage(setup=setup2)

    setup3 = MultiStageExperimentSetup(
        name="multistage_test",
        configuration_path=conf_path,
        script_path=script_path,
        input_path=None,
        output_path=str(stage_one_output_path),
        stage_name="stage_one"
    )
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    resume_stage(setup=setup3)
    resumed_metadata = json.load(open(os.path.join(str(stage_one_output_path), STAGE_METADATA)))
    assert len(metadata["exp_ids"]) + 2 == len(resumed_metadata["exp_ids"])
    assert resumed_metadata["steps"] == ["stage_one", "stage_one_resume_0", "stage_one_resume_1"]
