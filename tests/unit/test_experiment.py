import os
import copy
import pytest
from jikken.api import Experiment
import git


@pytest.fixture(autouse=True, scope='module')
def experiment_setup(tmpdir_factory):
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
    return expected_variables, tags, tmpdir


def test_experiment_equality(experiment_setup):
    # Given some variables and tags
    expected_variables, tags, tmpdir = experiment_setup
    # When I  create an experiment
    exp1 = Experiment("exp1", variables=expected_variables, code_dir=str(tmpdir), tags=tags)
    # And another one with teh same inputs
    exp2 = Experiment("exp1", variables=expected_variables, code_dir=str(tmpdir), tags=tags)
    # Then they are equal
    assert exp1 == exp2
    # And when i create a third one with an extra tag
    tags3 = tags + ["third tag"]
    exp3 = Experiment("exp1", variables=expected_variables, code_dir=str(tmpdir), tags=tags3)
    # Then that is also equal
    assert exp1 == exp3


def test_experiment_not_equality(experiment_setup):
    # Given some variables and tags
    expected_variables, tags, tmpdir = experiment_setup
    # When I  create an experiment
    exp1 = Experiment("exp1", variables=expected_variables, code_dir=str(tmpdir), tags=tags)
    # And whe I create one with a different name
    exp5 = Experiment("exp2", variables=expected_variables, code_dir=str(tmpdir), tags=tags)
    # Then it is not equal
    assert exp1 != exp5
    # And when I create one with different variables
    new_variables = copy.deepcopy(expected_variables)
    new_variables["training_parameters"]["batch_size"] = 5
    exp4 = Experiment("exp1", variables=new_variables, code_dir=str(tmpdir), tags=tags)
    # Then it is not equal
    assert exp1 != exp4


@pytest.fixture(autouse=True)
def jikken_experiment(experiment_setup):
    expected_variables, tags, tmpdir = experiment_setup
    repo_dir = str(tmpdir)
    file_name = os.path.join(repo_dir, 'new-file')
    r = git.Repo.init(repo_dir)
    # This function just creates an empty file ...
    open(file_name, 'wb').close()
    r.index.add([file_name])
    r.index.commit("initial commit")
    exp = Experiment(name="exp", variables=expected_variables, code_dir=repo_dir, tags=tags)
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
    assert exp.schema_hash == expected_hash
    exp_2 = Experiment(name="exp1", variables=expected_variables, code_dir=tmpdir.strpath)
    assert exp_2.schema_hash == exp.schema_hash


def test_experiment_parameters_schema(jikken_experiment):
    "test schema with parameters is constructed properly"
    exp, expected_variables, _, tmpdir = jikken_experiment
    expected_hash = '77c861c501833128e1cfb5b398588a7e'
    assert exp.parameters_hash == expected_hash


def test_experiment_parameters_schema_comparison(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    diff_variables = copy.deepcopy(expected_variables)
    diff_variables['training_parameters']['batch_size'] = 200
    exp_2 = Experiment(name="exp2", variables=diff_variables, code_dir=tmpdir.strpath)
    assert exp_2.schema_hash == exp.schema_hash
    assert exp.parameters_hash != exp_2.parameters_hash


def text_same_experiment_hash(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    exp_same = Experiment(variables=expected_variables, code_dir=tmpdir.strpath)
    assert exp.hash == exp_same.hash
    assert exp.parameters_hash == exp_same.parameters_hash
    assert exp.schema_hash == exp_same.schema_hash


def text_experiment_different_hash(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    exp_diff_dir = Experiment(variables=expected_variables, code_dir=os.getcwd())
    assert exp.parameters_hash == exp_diff_dir.parameters_hash
    assert exp.schema_hash == exp_diff_dir.schema_hash
    assert exp_diff_dir.hash != exp.hash
    diff_variables = copy.deepcopy(expected_variables)
    diff_variables['training_parameters']['batch_size'] = 200
    exp_diff_variables = Experiment(name="exp1", variables=diff_variables, code_dir=tmpdir.strpath)
    assert exp.parameters_hash != exp_diff_dir.parameters_hash
    assert exp.schema_hash == exp_diff_dir.schema_hash
    assert exp_diff_variables.hash != exp.hash


def test_experiment_different_tags_hash(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    exp_diff_tags = Experiment(name="exp", variables=expected_variables, code_dir=tmpdir.strpath, tags='test2')
    assert exp.schema_hash == exp_diff_tags.schema_hash
    assert exp.parameters_hash == exp_diff_tags.parameters_hash
    assert exp.hash == exp_diff_tags.hash


def test_experiment_different_names(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    exp_diff_tags = Experiment(name="exp1", variables=expected_variables, code_dir=tmpdir.strpath, tags='test2')
    assert exp.schema_hash == exp_diff_tags.schema_hash
    assert exp.parameters_hash == exp_diff_tags.parameters_hash
    assert exp.hash != exp_diff_tags.hash


def test_experiment_from_dict_is_same(jikken_experiment):
    exp, expected_variables, _, tmpdir = jikken_experiment
    new_exp = Experiment.from_dict(exp.to_dict())
    assert new_exp == exp
