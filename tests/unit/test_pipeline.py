import pytest
from jikken.experiment import Experiment
from jikken.pipeline import Pipeline


@pytest.fixture
def create_one_experiment(tmpdir):
    new_dir = tmpdir.mkdir("step_{}".format(0))
    variables = {"single_variable": 0}
    return Experiment(variables=variables, code_dir=str(new_dir))


@pytest.fixture
def create_multiple_experiments(tmpdir):
    results = []
    for index in range(1, 10):
        new_dir = tmpdir.mkdir("step_{}".format(index))
        variables = {"single_variable": index}
        results.append(Experiment(variables=variables, code_dir=str(new_dir)))
    return results


@pytest.fixture
def setup_pipeline(create_multiple_experiments):
    pipeline = Pipeline(name="testname")
    last_step_hash = ""
    for index, experiment in enumerate(create_multiple_experiments):
        pipeline.add(experiment, step_name="step_{}".format(index), last_step_hash=last_step_hash)
        last_step_hash = pipeline.hash()
    return pipeline


def test_pipeline_append_experiments(setup_pipeline, create_multiple_experiments):
    # Given a pipeline with multiple experiments
    step_hashes = []
    # When I iterate throught the pipeline
    for index, ((step_name, pipe_exp), expected_exp) in enumerate(zip(setup_pipeline, create_multiple_experiments)):
        step_hashes.append(setup_pipeline.hash(step_name))
        # Then the exps are yielded in the same order they were added
        assert pipe_exp == expected_exp
    # And every every pipeline step hash is unique
    assert len(step_hashes) == len(set(step_hashes))
    # And the last hash is the pipeline hash
    assert step_hashes[-1] == setup_pipeline.hash()


def test_pipeline_add_one_experiment(setup_pipeline, create_one_experiment):
    # Given a pipeline with multiple experiments
    hash = setup_pipeline.hash()
    current_step = setup_pipeline.last_step
    # When I add a new experiment
    setup_pipeline.add(create_one_experiment, 'last_experiment', hash)
    # Then the new hash changes
    new_hash = setup_pipeline.hash()
    assert hash != new_hash
    # And the last step changes
    assert current_step != setup_pipeline.last_step
    # And the previous hash can be recovered by the hash name
    assert hash == setup_pipeline.hash(current_step)


def test_add_one_experiment_with_wrong_last_hash(setup_pipeline, create_one_experiment):
    # given a pipeline with multiple experiments
    hash = setup_pipeline.hash()
    setup_pipeline.add(create_one_experiment, 'last_experiment', hash)

    # When I add a new experiment with the wrong last_step_hash
    with pytest.raises(ValueError):
        # Then I raise a ValueError
        setup_pipeline.add(create_one_experiment, 'last_experiment', hash)
