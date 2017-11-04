import os
from collections import namedtuple
from configparser import ConfigParser

JikkenConfig = namedtuple("JikkenConfig", ['db_path', 'db_type'])

DEFAULT_FILE = \
    """
    [db]
    path = ~/.jikken/jikken_db/
    type = tiny
    """

DEFAULT_PATH = '~/.jikken/config'


def write_default_config(config_file):
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w') as file_handle:
        file_handle.writelines(DEFAULT_FILE)


#TODO manage handling of local configs
def get_config():
    parser = ConfigParser()
    config_file = os.path.expanduser(DEFAULT_PATH)
    if not os.path.exists(config_file):
        write_default_config(config_file=config_file)
    parser.read(config_file)
    db_path = os.path.expanduser(parser['db']['path'])
    db_type = parser['db']['type']
    return JikkenConfig(db_type=db_type, db_path=db_path)
