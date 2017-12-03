import pytest
from jikken import MultiStageExperiment
from jikken.database import ExperimentQuery, MultiStageExperimentQuery
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
def db_one_multistage(jikken_db, one_multistage):
    _id = jikken_db.add(one_multistage)
    yield jikken_db, _id


@pytest.fixture()
def db_five_multistage(jikken_db, five_multistage):
    for ms in five_multistage:
        _id = jikken_db.add(ms)
    yield jikken_db


@pytest.fixture()
def db_three_experiments(jikken_db, multiple_experiments):
    for index, exp in enumerate(multiple_experiments):
        if index == 3:
            break
        jikken_db.add(exp)

    yield jikken_db


@pytest.fixture(params=['experiment', 'multistage'])
def all(request, one_experiment, one_multistage):
    """
    This is a workaround to create params out of fixtures
    see https://stackoverflow.com/questions/24340681/how-to-concatenate-several-parametrized-fixtures-into-a-new-fixture-in-py-test
    maybe one day it will be added to pytest see: https://github.com/pytest-dev/pytest/issues/349
    """
    if request.param == 'experiment':
        return one_experiment, "experiment"
    else:
        return one_multistage, "multistage"


def test_add_raises(jikken_db_session):
    """add should raise an error if object is not Experiment"""
    with pytest.raises(TypeError):
        jikken_db_session.add('hello world')


def test_delete_raises_no_id(db_one_experiment):
    """add should raise an error if we delete an id that doesn't exist"""
    db, _id = db_one_experiment
    new_id = "hello"
    with pytest.raises(KeyError):
        db.delete(new_id)


def test_add_and_return_valid_id(jikken_db, all):
    """DataBase.add(<valid exp>) should return an integer."""
    # GIVEN an initialized jikken db
    # WHEN a new jikken is added
    # THEN returned task_id is of type int
    doc, _ = all
    _id = jikken_db.add(doc)
    assert isinstance(_id, str)


def test_added_doc_has_id_set(jikken_db, all):
    """Make sure the id field is set by DataBase.add()."""
    # GIVEN an initialized db
    # AND a new  doc is added
    doc, doc_type = all
    _id = jikken_db.add(doc)

    # WHEN doc is retrieved
    doc_from_db = jikken_db.get(_id, doc_type)

    # THEN doc_id matches id field
    assert str(doc_from_db['id']) == _id


def test_added_doc_is_the_same(jikken_db, all):
    """make sure the restored document is the same except the doc_id"""
    # GIVEN an initialized db
    # AND a new  doc is added
    doc, doc_type = all
    _id = jikken_db.add(doc)

    # WHEN doc is retrieved
    doc_from_db = jikken_db.get(_id, doc_type)
    # AND contents are equivalent (except for id)
    exp_doc_dict = doc.to_dict()
    exp_doc_dict.pop('id')
    doc_from_db.pop('id')
    for key in doc_from_db:
        if key != "experiments":
            assert doc_from_db[key] == exp_doc_dict[key]
        else:
            for experiment, expected_experiment in zip(doc_from_db["experiments"], exp_doc_dict["experiments"]):
                _id = experiment[1].pop("id")
                expected_experiment[1].pop("id")
                # And the id has been changed from None to a hex string
                assert isinstance(_id, str)
                assert experiment == expected_experiment


def test_doc_retrieved_from_db_same(jikken_db, all):
    """When I restore a document it is the same from the db"""
    doc, doc_type = all
    _id = jikken_db.add(doc)
    # WHEN doc is retrieved
    doc_from_db = jikken_db.get(_id, doc_type)

    # Then they are equivalent
    new_doc = None
    if doc_type == "experiment":
        new_doc = Experiment.from_dict(doc_from_db)
    elif doc_type == "multistage":
        new_doc = MultiStageExperiment.from_dict(doc_from_db)
    assert doc == new_doc


def test_add_increases_count(db_multiple_experiments, tmpdir):
    """Test DataBase.add() affect on DataBase.count()."""
    # GIVEN a db with 9 experiments
    # WHEN another experiment is added
    db = db_multiple_experiments
    current_count = db.count()
    code_dir = tmpdir.mkdir("new_exp")
    db.add(Experiment(name="exp_4", variables={"index": 4}, code_dir=str(code_dir), tags=["tag_4"]))

    # THEN the count increases by 1
    assert db.count() == current_count + 1


def test_delete_experiments(db_three_experiments, tmpdir):
    """Test Database.delete and delete_all affect on database.count()"""
    # GIVEN a db with 3 experiments
    db = db_three_experiments
    experiment_count = db.count()
    # When we add one
    code_dir = tmpdir.mkdir("new_experiment")
    _id = db.add(Experiment(name="exp_4", variables={"index": 4}, code_dir=str(code_dir), tags=["tag_4"]))
    # AND we delete it
    db.delete(_id)
    # THEN the count remains 3
    assert db.count() == experiment_count
    # AND if we delete everything
    db.delete_all()
    # THEN the count goes to zero:
    assert db.count() == 0


def test_delete_mse_experiment(jikken_db, one_multistage):
    doc_id = jikken_db.add(one_multistage)
    count = jikken_db.count()
    assert count == 10
    jikken_db.delete(doc_id, doc_type="multistage")
    count = jikken_db.count()
    assert count == 0


def test_add_experiment_to_mse_already_in_db(jikken_db, one_experiment, one_multistage):
    doc_id = jikken_db.add(one_multistage)
    count = jikken_db.count()
    assert count == 10
    multistage = jikken_db.get(doc_id=doc_id, doc_type="multistage")
    new_multistage = MultiStageExperiment.from_dict(multistage)
    new_multistage.add(one_experiment, "stage_9", one_multistage.hash())
    mse_id = jikken_db.add(new_multistage)
    new_count = jikken_db.count()
    assert new_count == count + 2
    # db_mse = jikken_db.get(mse_id)


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
    db.add(Experiment(name="exp_4", variables={"index": 4}, code_dir=str(code_dir), tags=["tag_4"]))
    #  THEN list_experiments should return 4 experiments
    experiments = db.list_experiments()
    assert len(experiments) == 4

    # And if we query with tags <and> we should get 1 experiment
    query = ExperimentQuery(tags=["tag_1", "tag_2"], query_type="all")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 1

    # And if we query with tags <or> we should get 2 experiments
    query = ExperimentQuery(tags=["tag_1", "tag_2"], query_type="any")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 2
    # And if I query with parameter hashes <or> I should get 2 experiments
    schema_parameter_hashes = ['4c48b5e07e377d8293f2ef196e077d6a', '9e77300cedbcf7deac233fb814b0be96']
    query = ExperimentQuery(tags=["tag_1", "tag_2"], schema_param_hashes=schema_parameter_hashes, query_type="any")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 2

    # And if I query with parameter hashes <and> I should get 1 experiments
    query = ExperimentQuery(tags=["tag_1", "tag_2"], schema_param_hashes=schema_parameter_hashes, query_type="all")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 1

    # And if I query with tags that don't mach I should get no results
    query = ExperimentQuery(tags=["tag_3"], schema_param_hashes=schema_parameter_hashes, query_type="any")
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 0

    # And if i query with names  where only one existsI should get 1 result
    query = ExperimentQuery(names=["exp_4", "exp_5"])
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 1

    # And if I query with multiple names I get all matching names
    query = ExperimentQuery(names=["exp_1", "exp_2", "exp_3"])
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 3

    # And if I query with multiple names and tags I only get the exp that matches both name and tags
    query = ExperimentQuery(names=["exp_1", "exp_1", "exp_3"], tags=["tag_2"])
    experiments = db.list_experiments(query=query)
    assert len(experiments) == 1


@pytest.mark.test_listing
def test_list_ms_experiments_one_experiment_is_returned_properly(db_one_multistage):
    # Given a database with one mse inside
    db, id = db_one_multistage
    # When I query the db
    mse_experiments = db.list_ms_experiments()
    #  Then I get back the one mse
    assert len(mse_experiments) == 1
    # And when I query the experiments
    experiments = db.list_experiments()
    # Then I get back all the experiments of the mse
    assert len(experiments) == 9
    # And When I query the MSE by id
    query = MultiStageExperimentQuery(ids=[id])
    # Then I get back the mse
    mse_experiments = db.list_ms_experiments(query=query)
    assert len(mse_experiments) == 1
    # And I check that all steps have the experiments retrieved and not their ids
    for mse in mse_experiments:
        for (key, exp) in mse['experiments']:
            assert isinstance(exp, dict)
            assert exp['type'] == 'experiment'


@pytest.mark.test_listing
def test_list_ms_experiments(db_five_multistage, tmpdir):
    # Given a database with five mse inside
    db = db_five_multistage
    # When I query the db
    mse_experiments = db.list_ms_experiments()
    #  Then I get back the five mse
    assert len(mse_experiments) == 5

    # And When I query the MSE by names
    query = MultiStageExperimentQuery(names=["testname_1", "testname_2", "wrong_name"])
    # Then I get back the  2 mse
    mse_experiments = db.list_ms_experiments(query=query)
    assert len(mse_experiments) == 2

    # And when I query by steps  and I get all mses that match all of those  steps
    query = MultiStageExperimentQuery(steps=["step_4", "step_5", "step_8"])
    # Then I get back the  2 mse
    # the first one has from 1-9, the second from 4-13, the third from 8-17, etc.
    mse_experiments = db.list_ms_experiments(query=query)
    assert len(mse_experiments) == 2

    # And when I query by steps (or) I get all mses that have any of  steps
    query = MultiStageExperimentQuery(steps=["step_4", "step_5", "step_8"], query_type="any")
    # Then I get back the  2 mse
    # the first one has from 1-9, the second from 4-13, the third from 8-17, etc.
    mse_experiments = db.list_ms_experiments(query=query)
    assert len(mse_experiments) == 3


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
    exp = db.get(_id, "experiment")
    # Then the stdout or stderr key is updated
    assert exp[std_type] == new_string
    # And when I append a new string
    new_string_2 = "this is a second string"
    db.update_std(_id, new_string_2, std_type)
    exp = db.get(_id, "experiment")
    # Then the new string gets updated
    assert exp[std_type] == new_string + new_string_2


def test_update_std_raises(db_one_experiment):
    # Given a db with one experiment
    db, _id = db_one_experiment
    # When I update the std with the wrong stream type
    new_string = "this is a string"
    # Then the db raises a Value error
    with pytest.raises(ValueError):
        db.update_std(_id, new_string, 'error')


monitored_params = [
    (["hello", "bye"]),
    ([1.1, 2.2]),
    ([[1, 2], [3, 4]])

]


@pytest.mark.parametrize("monitored_inputs", monitored_params, ids=["string", "int", "list"])
def test_updated_monitored(monitored_inputs, db_one_experiment):
    # Given a db with one experiment
    db, _id = db_one_experiment

    key = "test_var"
    value = monitored_inputs[0]
    # When I update a new value
    db.update_monitored(_id, key=key, value=value)
    # Then it gets created as a list
    exp = db.get(_id, "experiment")
    # assert exp['monitored'][key] == [monitored_inputs[0]]
    # and when I update the same key
    value = monitored_inputs[1]
    # When I update a new value
    db.update_monitored(_id, key=key, value=value)
    # Then the new value gets appended
    exp = db.get(_id, "experiment")
    assert exp['monitored'][key] == monitored_inputs


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
    exp = db.get(_id, "experiment")
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
