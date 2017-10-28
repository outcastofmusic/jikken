import os
import copy
import pytest
from jikken.api import Experiment


@pytest.fixture(autouse=True, scope='module')
def jikken_experiment(tmpdir_factory):
    expected_variables = {
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
    tags = ['test', 'simple']
    tmpdir = tmpdir_factory.mktemp('mydir')
    exp = Experiment(variables=expected_variables, code_dir=tmpdir, tags=tags)
    return exp, expected_variables, tags, tmpdir


def test_experiment_variables(jikken_experiment):
    "test variables are initialized properly and are not settable"
    exp, expected_variables, *_ = jikken_experiment
    assert exp.variables == expected_variables
    with pytest.raises(AttributeError):
        exp.variables = expected_variables


def test_experiment_tags(jikken_experiment):
    "test tags are initialized properly and are not settable"
    exp, _, expected_tags, _ = jikken_experiment
    assert exp.tags == expected_tags
    with pytest.raises(AttributeError):
        exp.tags = expected_tags


def test_experiment_schema(jikken_experiment):
    "test schema is constructed properly"
    exp, expected_variables, _, tmpdir = jikken_experiment
    expected_hash = '40a3f5106cf9426bd4b13b168717e7bf'
    assert exp.experiment_schema_hash == expected_hash
    exp_2 = Experiment(variables=expected_variables, code_dir=tmpdir)
    assert exp_2.experiment_schema_hash == exp.experiment_schema_hash


def test_experiment_parameters_schema(jikken_experiment):
    "test schema with parameters is constructed properly"
    exp, expected_variables, _, tmpdir = jikken_experiment
    expected_hash = '77c861c501833128e1cfb5b398588a7e'
    assert exp.experiment_parameters_hash == expected_hash


def test_experiment_parameters_schema_comparison(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    diff_variables = copy.deepcopy(expected_variables)
    diff_variables['training_parameters']['batch_size'] = 200
    exp_2 = Experiment(variables=diff_variables, code_dir=tmpdir)
    assert exp_2.experiment_schema_hash == exp.experiment_schema_hash
    assert exp.experiment_parameters_hash != exp_2.experiment_parameters_hash


def text_same_experiment_hash(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    exp_same = Experiment(variables=expected_variables, code_dir=tmpdir)
    assert exp.hash == exp_same.hash
    assert exp.experiment_parameters_hash == exp_same.experiment_parameters_hash
    assert exp.experiment_schema_hash == exp_same.experiment_schema_hash


def text_experiment_diffent_hash(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    exp_diff_dir = Experiment(variables=expected_variables, code_dir=os.getcwd())
    assert exp.experiment_parameters_hash == exp_diff_dir.experiment_parameters_hash
    assert exp.experiment_schema_hash == exp_diff_dir.experiment_schema_hash
    assert exp_diff_dir.hash != exp.hash
    diff_variables = copy.deepcopy(expected_variables)
    diff_variables['training_parameters']['batch_size'] = 200
    exp_diff_variables = Experiment(variables=diff_variables, code_dir=tmpdir)
    assert exp.experiment_parameters_hash != exp_diff_dir.experiment_parameters_hash
    assert exp.experiment_schema_hash == exp_diff_dir.experiment_schema_hash
    assert exp_diff_variables.hash != exp.hash


def test_experiment_different_tags_hash(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    exp_diff_tags = Experiment(variables=expected_variables, code_dir=tmpdir, tags='test2')
    assert exp.experiment_schema_hash == exp_diff_tags.experiment_schema_hash
    assert exp.experiment_parameters_hash == exp_diff_tags.experiment_parameters_hash
    assert exp.hash == exp_diff_tags.hash
