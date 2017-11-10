import os
from collections import namedtuple
from configparser import ConfigParser

JikkenConfig = namedtuple("JikkenConfig", ['db_path', 'db_type', 'db_name'])
JikkenConfig.__new__.__defaults__ = ("~/.jikken/jikken_db", "tiny", "jikken")

DEFAULT_FILE = \
    """
    [db]
    path = ~/.jikken/jikken_db/
    type = tiny
    name = jikken
    """

DEFAULT_PATH = '~/.jikken/config'


def write_default_config():
    config_file = os.path.expanduser(DEFAULT_PATH)
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w') as file_handle:
        file_handle.writelines(DEFAULT_FILE)
    return config_file


def read_config(config_file):
    parser = ConfigParser()
    parser.read(config_file)
    db_path = os.path.expanduser(parser['db']['path'])
    db_type = parser['db']['type']
    return JikkenConfig(db_type=db_type, db_path=db_path)


def get_config(config_file=None):
    if config_file is None or not os.path.exists(config_file):
        config_file = write_default_config()
    return read_config(config_file)
