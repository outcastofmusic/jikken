import json

import pytest

TEST_CONFIG_JSON = {
    "input_parameters": {
        "filepath": "/data",
        "preprocessing": True,
        "batch_size": 4,
        "transformations": [
            "stopwords",
            "tokenize",
            "remove_punct"
        ]
    },
    "training_parameters": {
        "algorithm": "Seq2Seq",
        "batch_size": 100,
        "attention": "multiplicative"
    }
}

TEST_SCRIPT=\
"""
import click
import json
@click.command()
@click.option('--configuration_path','-c', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=True))
def main(configuration_path):
    print(open(configuration_path).readlines())
    
if __name__ == '__main__':
    main()
"""

@pytest.fixture()
def file_setup(tmpdir):
    conf_file = tmpdir.join('configuration.json')
    conf_file.write(json.dumps(TEST_CONFIG_JSON))

    script_file = tmpdir.join('script.py')
    script_file.write(TEST_SCRIPT)
    return conf_file.strpath, script_file.strpath, TEST_CONFIG_JSON
