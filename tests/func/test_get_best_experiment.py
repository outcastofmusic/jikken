import pytest
from contextlib import contextmanager

import jikken
from jikken import Experiment
from jikken.database import ExperimentQuery
from jikken.api import get_best

from unittest.mock import MagicMock


@pytest.fixture()
def db_with_monitored_experiments(tmpdir, jikken_db, mocker):
    list_experiments_mock = MagicMock()

    def setup_database_stub(db):
        db.list_experiments = list_experiments_mock

        @contextmanager
        def db_stub():
            yield db

        return db_stub()

    results = []
    for index in range(1, 10):
        new_dir = tmpdir.mkdir("step_{}".format(index))
        variables = {"single_variable": index}
        tags = ["tag_{}".format(tag) for tag in range(index)]
        exp = Experiment(name="exp_{}".format(index), variables=variables, code_dir=str(new_dir), tags=tags).to_dict()
        exp["id"] = index
        exp['monitored'] = {"valid_loss": [i for i in range(index + 5, index + 15)], "final_value": 10 - index}
        results.append(exp)
    list_experiments_mock.return_value = results
    mocker.patch.object(jikken.api, 'setup_database', return_value=setup_database_stub(jikken_db))
    yield


exp_values = [
    # optimum, name, metric
    ("min", "exp_1", "valid_loss"),
    ("max", "exp_9", "valid_loss"),
    ("max", "exp_1", "final_value"),
    ("min", "exp_9", "final_value"),
    ("min", None, "doesnt_exist"),
]


@pytest.mark.parametrize("optimum, name, metric", exp_values)
def test_get_best_experiment(optimum, name, metric, db_with_monitored_experiments):
    # Given a mock database with experiments with monitored values
    query = ExperimentQuery()
    # When I query for a metric and an optimum
    result = get_best(query=query, metric=metric, optimum=optimum)
    # Then I get the one with the expected value
    if name is not None:
        assert result['name'] == name
    else:
        # And when I query with a non existent monitor
        # Then I get None  s a result
        assert result is None
