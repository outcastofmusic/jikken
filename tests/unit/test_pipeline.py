import pytest




def test_pipeline_append_experiments(one_pipeline, multiple_experiments):
    # Given a pipeline with multiple experiments
    step_hashes = []
    # When I iterate throught the pipeline
    for index, ((step_name, pipe_exp), expected_exp) in enumerate(zip(one_pipeline, multiple_experiments)):
        step_hashes.append(one_pipeline.hash(step_name))
        # Then the exps are yielded in the same order they were added
        assert pipe_exp == expected_exp
    # And every every pipeline step hash is unique
    assert len(step_hashes) == len(set(step_hashes))
    # And the last hash is the pipeline hash
    assert step_hashes[-1] == one_pipeline.hash()


def test_pipeline_add_one_experiment(one_pipeline, one_experiment):
    # Given a pipeline with multiple experiments
    hash = one_pipeline.hash()
    current_step = one_pipeline.last_step
    # When I add a new experiment
    one_pipeline.add(one_experiment, 'last_experiment', hash)
    # Then the new hash changes
    new_hash = one_pipeline.hash()
    assert hash != new_hash
    # And the last step changes
    assert current_step != one_pipeline.last_step
    # And the previous hash can be recovered by the hash name
    assert hash == one_pipeline.hash(current_step)


def test_add_one_experiment_with_wrong_last_hash(one_pipeline, one_experiment):
    # given a pipeline with multiple experiments
    hash = one_pipeline.hash()
    one_pipeline.add(one_experiment, 'last_experiment', hash)

    # When I add a new experiment with the wrong last_step_hash
    with pytest.raises(ValueError):
        # Then I raise a ValueError
        one_pipeline.add(one_experiment, 'last_experiment', hash)
