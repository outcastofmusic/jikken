import pytest
from jikken.database import ExperimentQuery
from jikken.experiment import Experiment


@pytest.fixture()
def db_one_experiment(jikken_db, one_experiment):
    _id = jikken_db.add(one_experiment)
    yield jikken_db, _id


@pytest.fixture()
def db_multiple_experiments(jikken_db, multiple_experiments):
    for exp in multiple_experiments:
        jikken_db.add(exp)
    yield jikken_db


@pytest.fixture()
def db_three_experiments(jikken_db, multiple_experiments):
    for index, exp in enumerate(multiple_experiments):
        if index == 3:
            break
        jikken_db.add(exp)

    yield jikken_db


def test_add_raises(jikken_db_session):
    """add should raise an error if object is not Experiment"""
    with pytest.raises(TypeError):
        jikken_db_session.add('hello world')


def test_delete_raises_no_id(db_one_experiment):
    db, _id = db_one_experiment
    new_id = "hello"
    with pytest.raises(KeyError):
        db.delete(new_id)


def test_add_and_return_valid_id(jikken_db, one_experiment):
    """DataBase.add(<valid exp>) should return an integer."""
    # GIVEN an initialized jikken db
    # WHEN a new jikken is added
    # THEN returned task_id is of type int
    _id = jikken_db.add(one_experiment)
    assert isinstance(_id, str)


def test_added_task_has_id_set(jikken_db, one_experiment):
    """Make sure the id field is set by DataBase.add()."""
    # GIVEN an initialized tasks db
    #   AND a new task is added

    _id = jikken_db.add(one_experiment)

    # WHEN experiment is retrieved
    exp_from_db = jikken_db.get(_id)

    # THEN experiment_id matches id field
    assert str(exp_from_db['id']) == _id

    # AND contents are equivalent (except for id)
    nex_exp_dict = one_experiment.to_dict()
    nex_exp_dict.pop('id')
    exp_from_db.pop('id')
    assert exp_from_db == nex_exp_dict


def test_add_increases_count(db_multiple_experiments, tmpdir):
    """Test DataBase.add() affect on DataBase.count()."""
    # GIVEN a db with 9 experiments
    # WHEN another experiment is added
    db = db_multiple_experiments
    current_count = db.count()
    code_dir = tmpdir.mkdir("new_exp")
    db.add(Experiment(variables={"index": 4}, code_dir=str(code_dir), tags=["tag_4"]))

    # THEN the count increases by 1
    assert db.count() == current_count + 1


def test_delete_experiments(db_three_experiments, tmpdir):
    """Test Database.delete and delete_all affect on database.count()"""
    # GIVEN a db with 3 experiments
    db = db_three_experiments
    experiment_count = db.count()
    # When we add one
    code_dir = tmpdir.mkdir("new_experiment")
    _id = db.add(Experiment(variables={"index": 4}, code_dir=str(code_dir), tags=["tag_4"]))
    # AND we delete it
    db.delete(_id)
    # THEN the count remains 3
    assert db.count() == experiment_count
    # AND if we delete everything
    db.delete_all()
    # THEN the count goes to zero:
    assert db.count() == 0


def test_multiple_experiments_have_same_schema(db_multiple_experiments):
    expected_schema = '03872a0ac84ba17173ae79a9a5c4425b'
    # GIVEN multiple experiments with the same variables
    db = db_multiple_experiments
    #  WHEN I check the schema hash
    experiments = db.list_experiments()
    # THEN all schemas should be the same
    for exp in experiments:
        assert exp['schema_hash'] == expected_schema


@pytest.mark.test_listing
def test_list_experiments(db_three_experiments, tmpdir):
    """Test  DataBase.add() affects list_experiments"""
    # GIVEN a db with 3 experiments
    # When another experiment is added
    db = db_three_experiments
    code_dir = tmpdir.mkdir("new_experiment")
    db.add(Experiment(variables={"index": 4}, code_dir=str(code_dir), tags=["tag_4"]))
    #  THEN list_experiments should return 4 experiments
    experiments = db.list_experiments()
    assert len(experiments) == 4

    # And if we query with tags <and> we should get 1 experiment
    query = ExperimentQuery(tags=["tag_1", "tag_2"], query_type="and")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 1

    # And if we query with tags <or> we should get 2 experiments
    query = ExperimentQuery(tags=["tag_1", "tag_2"], query_type="or")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 2
    # And if I query with parameter hashes <or> I should get 2 experiments
    schema_parameter_hashes = ['4c48b5e07e377d8293f2ef196e077d6a', '9e77300cedbcf7deac233fb814b0be96']
    query = ExperimentQuery(tags=["tag_1", "tag_2"], schema_param_hashes=schema_parameter_hashes, query_type="or")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 2

    # And if I query with parameter hashes <and> I should get 1 experiments
    query = ExperimentQuery(tags=["tag_1", "tag_2"], schema_param_hashes=schema_parameter_hashes, query_type="and")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 1

    query = ExperimentQuery(tags=["tag_3"], schema_param_hashes=schema_parameter_hashes, query_type="or")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 0


std_options = [
    # std_type
    ("stdout"),
    ("stderr"),
]


@pytest.mark.parametrize("std_type", std_options)
def test_update_std_experiments(std_type, db_one_experiment):
    # Given a db with one experiment
    db, _id = db_one_experiment
    # When I update the stdout or stderr
    new_string = "this is a string"
    db.update_std(_id, new_string, std_type)
    # And I retrieve the experiment
    exp = db.get(_id)
    # Then the stdout or stderr key is updated
    assert exp[std_type] == new_string


def test_update_std_raises(db_one_experiment):
    # Given a db with one experiment
    db, _id = db_one_experiment
    # When I update the std with the wrong stream type
    new_string = "this is a string"
    # Then the db raises a Value error
    with pytest.raises(ValueError):
        db.update_std(_id, new_string, 'error')


status_options = [
    # status
    ('created'),
    ('running'),
    ('completed'),
    ('error')

]


@pytest.mark.parametrize("status", status_options)
def test_update_status_experiments(status, db_one_experiment):
    # Given a db with one experiment
    db, _id = db_one_experiment
    # When I update the status
    db.update_status(_id, status)
    # And I retrieve the experiment
    exp = db.get(_id)
    # Then status is updated
    assert exp['status'] == status


def test_update_status_raises(db_one_experiment):
    # Given a db with 1 experiment
    db, _id = db_one_experiment
    # When I update the status
    status = "not a status"
    # Then db raises an error
    with pytest.raises(ValueError):
        db.update_status(_id, status)
