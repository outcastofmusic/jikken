import pytest
from jikken import MultiStageExperiment


def test_multistage_append_experiments(one_multistage, multiple_experiments):
    # Given a multistage with multiple experiments
    step_hashes = []
    # When I iterate throught the multistage
    for index, ((step_name, pipe_exp), expected_exp) in enumerate(zip(one_multistage, multiple_experiments)):
        step_hashes.append(one_multistage.hash(step_name))
        # Then the exps are yielded in the same order they were added
        assert pipe_exp == expected_exp
    # And every every multistage step hash is unique
    assert len(step_hashes) == len(set(step_hashes))
    # And the last hash is the multistage hash
    assert step_hashes[-1] == one_multistage.hash()


def test_multistage_add_one_experiment(one_multistage, one_experiment):
    # Given a multistage with multiple experiments
    hash = one_multistage.hash()
    current_step = one_multistage.last_stage
    # When I add a new experiment
    one_multistage.add(one_experiment, 'last_experiment', hash)
    # Then the new hash changes
    new_hash = one_multistage.hash()
    assert hash != new_hash
    # And the last step changes
    assert current_step != one_multistage.last_stage
    # And the previous hash can be recovered by the hash name
    assert hash == one_multistage.hash(current_step)


def test_add_one_experiment_with_wrong_last_hash(one_multistage, one_experiment):
    # given a multistage with multiple experiments
    hash = one_multistage.hash()
    one_multistage.add(one_experiment, 'last_experiment', hash)

    # When I add a new experiment with the wrong last_step_hash
    with pytest.raises(ValueError):
        # Then I raise a ValueError
        one_multistage.add(one_experiment, 'last_experiment', hash)


def test_multistage_from_dict(one_multistage):
    new_multistage = MultiStageExperiment.from_dict(one_multistage.to_dict())
    assert new_multistage == one_multistage
