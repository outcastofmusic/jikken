import pytest
from jikken.database import DataBase
from jikken.experiment import Experiment


# @pytest.fixture(scope='session')
# def jikken_db_session(tmpdir_factory):
#     """Connect to db before tests, disconnect after."""
#     temp_dir = tmpdir_factory.mktemp('temp')
#     test_database = DataBase(db_path=str(temp_dir), db_type='tiny')
#     yield test_database
#     test_database.stop_db()
#
#
# @pytest.fixture()
# def jikken_db(jikken_db_session):
#     yield jikken_db_session
#     jikken_db_session.delete_all()


@pytest.fixture()
def add_one_experiment(jikken_db, file_setup):
    code_dir = file_setup[0]
    index = 0
    _id = jikken_db.add(
        Experiment(variables={"index": index}, code_dir=code_dir, tags=["tag_" + str(i) for i in range(index + 1)])
    )
    yield jikken_db, _id


@pytest.fixture()
def add_multiple_experiments(jikken_db, file_setup):
    code_dir = file_setup[0]
    for index in range(3):
        jikken_db.add(
            Experiment(variables={"index": index}, code_dir=code_dir, tags=["tag_" + str(i) for i in range(index + 1)])
        )
    yield jikken_db, file_setup


def test_add_raises(jikken_db_session):
    """add should raise an error if object is not Experiment"""
    with pytest.raises(TypeError):
        jikken_db_session.add('hello world')


def test_delete_raises_no_id(add_one_experiment):
    jikken_db, _id = add_one_experiment
    with pytest.raises(KeyError):
        jikken_db.delete(_id + 1)


def test_add_and_return_valid_id(jikken_db, file_setup):
    """DataBase.add(<valid exp>) should return an integer."""
    # GIVEN an initialized jikken db
    # WHEN a new jikken is added
    # THEN returned task_id is of type int
    code_dir = file_setup[0]
    new_exp = Experiment(variables={'val1': 'do something'}, code_dir=code_dir)
    _id = jikken_db.add(new_exp)
    assert isinstance(_id, int)


@pytest.mark.smoke
def test_added_task_has_id_set(jikken_db, file_setup):
    """Make sure the id field is set by DataBase.add()."""
    # GIVEN an initialized tasks db
    #   AND a new task is added

    code_dir = file_setup[0]
    new_exp = Experiment(variables={'val1': 'do something'}, code_dir=code_dir)
    _id = jikken_db.add(new_exp)

    # WHEN experiment is retrieved
    exp_from_db = jikken_db.get(_id)

    # THEN experiment_id matches id field
    assert exp_from_db['id'] == _id

    # AND contents are equivalent (except for id)
    nex_exp_dict = new_exp.to_dict()
    nex_exp_dict.pop('id')
    exp_from_db.pop('id')
    assert exp_from_db == nex_exp_dict


def test_add_increases_count(add_multiple_experiments):
    """Test DataBase.add() affect on DataBase.count()."""
    # GIVEN a db with 3 experiments
    # WHEN another experiment is added
    db, file_setup = add_multiple_experiments
    code_dir = file_setup[0]
    db.add(Experiment(variables={"index": 4}, code_dir=code_dir, tags=["tag_4"]))

    # THEN the count increases by 1
    assert db.count() == 4


def test_delete_experiments(add_multiple_experiments):
    """Test Database.delete and delete_all affect on database.count()"""
    # GIVEN a db with 3 experiments
    # When we add one
    db, file_setup = add_multiple_experiments
    code_dir = file_setup[0]
    _id = db.add(Experiment(variables={"index": 4}, code_dir=code_dir, tags=["tag_4"]))
    # AND we delete it
    db.delete(_id)
    # THEN the count remains 3
    assert db.count() == 3
    # AND if we delete everything
    db.delete_all()
    # THEN the count goes to zero:
    assert db.count() == 0


def test_list_experiments(add_multiple_experiments):
    """Test  DataBase.add() affects list_experiments"""
    # GIVEN a db with 3 experiments
    # When another experiment is added
    db, file_setup = add_multiple_experiments
    code_dir = file_setup[0]
    db.add(Experiment(variables={"index": 4}, code_dir=code_dir, tags=["tag_4"]))

    #  THEN list_experiments should return 4 experiments
    experiments = db.list_experiments()
    assert len(experiments) == 4

    # And if we query with tags <and> we should get 1 experiment
    experiments = db.list_experiments(tags=["tag_1", "tag_2"])
    assert len(experiments) == 1

    # And if we query with tags <or> we should get 2 experiments
    experiments = db.list_experiments(tags=["tag_1", "tag_2"], query_type='or')
    assert len(experiments) == 2


def test_update_std_experiments(add_one_experiment):
    # Given a db with one experiment
    db, _id = add_one_experiment
    # When I update the stdoutput
    new_string = "this is a string"
    db.update_std(_id, new_string, "stdout")
    # And I retrieve the experiment
    exp = db.get(_id)
    # Then the stdout key is updated
    assert exp['stdout'] == new_string