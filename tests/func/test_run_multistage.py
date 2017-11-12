import pytest

import json
from contextlib import contextmanager

import jikken
from jikken.api import run_multistage


def setup_database_stub(db):
    @contextmanager
    def db_stub():
        yield db

    return db_stub()


@pytest.mark.skip("not implemented yet")
def test_run_multistage_given_script_and_config(file_setup, capsys, jikken_db, mocker):
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    conf_path, script_path, config_json = file_setup
    run_multistage(configuration_path=conf_path, script_path=script_path, input_path=input_path,
                   output_path=output_path)
