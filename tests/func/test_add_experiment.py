import jikken
import pytest
from jikken import Experiment


def test_add_raises():
    """add should raise an error if object is not Experiment"""
    with pytest.raises(TypeError):
        jikken.add('hello world')


def test_add_and_return_valid_id(jikken_db, file_setup):
    """jikken.add(<valid task>) should return an integer."""
    # GIVEN an initialized jikken db
    # WHEN a new jikken is added
    # THEN returned task_id is of type int
    code_dir = file_setup[0]
    new_exp = Experiment(variables={'val1': 'do something'}, code_dir=code_dir)
    task_id = jikken.add(new_exp)
    assert isinstance(task_id, int)
