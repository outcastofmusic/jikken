import pytest
import os
from jikken.database.config import get_config, write_default_config, JikkenConfig, read_config


@pytest.fixture()
def home_dir(tmpdir, monkeypatch):
    home_dir = tmpdir.mkdir('home')
    monkeypatch.setenv('HOME', str(home_dir))
    return home_dir


def test_default_config_created(home_dir):
    config_file = write_default_config()
    assert config_file == os.path.join(str(home_dir), ".jikken", "config")


def test_read_default_config_file(home_dir):
    config_file = write_default_config()
    config = read_config(config_file)
    expected_config = JikkenConfig(db_type='tiny', db_path=os.path.join(str(home_dir), ".jikken", "jikken_db/"))
    assert config == expected_config


def test_load_local_config(home_dir, tmpdir):
    new_config_file = tmpdir.join("config")
    new_config = \
        """
        [db]
        path = jikken_db/
        type = mongo
        """
    with new_config_file.open('w') as file_handle:
        file_handle.write(new_config)

    config = get_config(str(new_config_file))
    expected_config = JikkenConfig(db_type='mongo', db_path="jikken_db/")
    assert config == expected_config
