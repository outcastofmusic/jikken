import json

import pytest
import click
from click.testing import CliRunner
from .mock_experiment import main_yaml, main_json, main_error, main_cli


class TestCli:
    @pytest.mark.parametrize("test_func", [
        main_yaml,
        main_json,
    ])
    def test_default_cli(self, test_func):
        results = test_func()
        expected_dict = {
            "training_parameters":
                {"batch_size": 100,
                 "algorithm": "Seq2Seq",
                 "attention": "multiplicative"
                 },
            "input_parameters":
                {'batch_size': 4,
                 "filepath": "/data",
                 "preprocessing": True,
                 "transformations": ["stopwords", "tokenize", "remove_punct"]
                 }

        }
        assert results == expected_dict

    def test_error_cli(self):
        with pytest.raises(IOError):
            results = main_error()

    def test_cli_experiment(self):
        runner = CliRunner()
        result = runner.invoke(main_cli, ["./tests/experiment.yaml", "experiment", "test"])
        assert result.exit_code == 0
        expected_dict = {
            "training_parameters":
                {"batch_size": 100,
                 "algorithm": "Seq2Seq",
                 "attention": "multiplicative"
                 },
            "input_parameters":
                {'batch_size': 4,
                 "filepath": "/data",
                 "preprocessing": True,
                 "transformations": ["stopwords", "tokenize", "remove_punct"]
                 }

        }
        assert json.loads(result.output) == expected_dict
