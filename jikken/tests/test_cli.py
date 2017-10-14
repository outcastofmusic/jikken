from .mock_experiment import main
import yaml
class TestCli:
    def test_default_cli(self):
        results = main()
        expected_dict = {
            "training_parameters":
                {"batch_size":100,
                 "algorithm": "Seq2Seq",
                 "attention": "multiplicative"
                 },
            "input_parameters":
                {'batch_size':4,
                 "filepath": "/data",
                 "preprocessing":True,
                 "transformations": ["stopwords", "tokenize", "remove_punct"]
                 }

        }
        assert results == expected_dict
