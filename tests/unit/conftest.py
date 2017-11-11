import pytest
from jikken.experiment import Experiment
from jikken.pipeline import Pipeline

@pytest.fixture
def one_experiment(tmpdir):
    new_dir = tmpdir.mkdir("step_{}".format(0))
    variables = {"single_variable": 0}
    return Experiment(variables=variables, code_dir=str(new_dir))


@pytest.fixture
def multiple_experiments(tmpdir):
    results = []
    for index in range(1, 10):
        new_dir = tmpdir.mkdir("step_{}".format(index))
        variables = {"single_variable": index}
        tags = ["tag_{}".format(tag) for tag in range(index)]
        results.append(Experiment(variables=variables, code_dir=str(new_dir), tags=tags))
    return results

@pytest.fixture
def one_pipeline(multiple_experiments):
    pipeline = Pipeline(name="testname")
    last_step_hash = ""
    for index, experiment in enumerate(multiple_experiments):
        experiment._id = index + 1
        pipeline.add(experiment, step_name="step_{}".format(index), last_step_hash=last_step_hash)
        last_step_hash = pipeline.hash()
    return pipeline