import pytest
from jikken.experiment import Experiment
from jikken.multistage import MultiStageExperiment


@pytest.fixture
def one_experiment(tmpdir):
    new_dir = tmpdir.mkdir("step_{}".format(0))
    variables = {"single_variable": 0}
    return Experiment(name="exp_{}".format(0), variables=variables, code_dir=str(new_dir))


@pytest.fixture
def multiple_experiments(tmpdir):
    results = []
    for index in range(1, 10):
        new_dir = tmpdir.mkdir("step_{}".format(index))
        variables = {"single_variable": index}
        tags = ["tag_{}".format(tag) for tag in range(index)]
        results.append(Experiment(name="exp_{}".format(index), variables=variables, code_dir=str(new_dir), tags=tags))
    return results


@pytest.fixture
def one_multistage(multiple_experiments):
    multistage = MultiStageExperiment(name="testname")
    last_step_hash = ""
    for index, experiment in enumerate(multiple_experiments):
        multistage.add(experiment, stage_name="step_{}".format(index), last_step_hash=last_step_hash)
        last_step_hash = multistage.hash()
    return multistage


@pytest.fixture
def five_multistage(multiple_experiments):
    ms_experiments = []
    for ms_index in range(5):
        multistage = MultiStageExperiment(name="testname_{}".format(ms_index))
        last_step_hash = ""
        for index, experiment in enumerate(multiple_experiments):
            step_index = ms_index * 4 + index
            multistage.add(experiment, stage_name="step_{}".format(step_index), last_step_hash=last_step_hash)
            last_step_hash = multistage.hash()
        ms_experiments.append(multistage)
    return ms_experiments
