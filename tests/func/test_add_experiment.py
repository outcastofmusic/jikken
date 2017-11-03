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
    _id = jikken.add(new_exp)
    assert isinstance(_id, int)

@pytest.mark.smoke
def test_added_task_has_id_set(jikken_db, file_setup):
    """Make sure the task_id field is set by tasks.add()."""
    # GIVEN an initialized tasks db
    #   AND a new task is added

    code_dir = file_setup[0]
    new_exp = Experiment(variables={'val1': 'do something'}, code_dir=code_dir)
    _id = jikken.add(new_exp)

    # WHEN task is retrieved
    exp_from_db = jikken.get(_id)

    # THEN task_id matches id field
    assert exp_from_db['id'] == _id

    # AND contents are equivalent (except for id)
    nex_exp_dict = new_exp.to_dict()
    nex_exp_dict.pop('id')
    exp_from_db.pop('id')
    assert exp_from_db == nex_exp_dict


# def test_add_increases_count(db_with_3_tasks):
#     """Test tasks.add() affect on tasks.count()."""
#     # GIVEN a db with 3 tasks
#     #  WHEN another task is added
#     tasks.add(Task('throw a party'))
#
#     #  THEN the count increases by 1
#     assert tasks.count() == 4

