import os
from contextlib import contextmanager
from collections import namedtuple

from jikken.experiment import Experiment
from jikken.multistage import MultiStageExperiment

from .config import get_config, JikkenConfig

ExperimentQuery = namedtuple("ExperimentQuery",
                             ["tags", "ids", "schema_hashes", "status", "schema_param_hashes", "query_type"])
ExperimentQuery.__new__.__defaults__ = (None, None, None, None, None, "and")


class Singleton(type):
    def __init__(self, *args, **kwargs):
        self._instance = None
        super(Singleton, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = super(Singleton, self).__call__(*args, **kwargs)
            return self._instance
        elif self._instance.db != kwargs['config'].db_type:
            self._instance = super(Singleton, self).__call__(*args, **kwargs)
            return self._instance
        else:
            return self._instance


class DataBase(metaclass=Singleton):
    def __init__(self, config: JikkenConfig):
        self.db = config.db_type
        if config.db_type == 'tiny':
            os.makedirs(config.db_path, exist_ok=True)
            from .db_tinydb import TinyDB
            self._database = TinyDB(config.db_path, config.db_name)
        elif config.db_type == 'mongo':
            from .db_mongo import MongoDB
            self._database = MongoDB(config.db_path, config.db_name)
        elif config.db_type == 'es':
            # TODO implement es
            raise NotImplementedError('ES not implemented yet')
        else:
            raise ValueError("db_type must be a 'tiny' or 'mongo'")

        if self._database is None:
            raise ConnectionError("could not connect to database")

    def add(self, data_object: (Experiment, MultiStageExperiment)) -> int:
        if isinstance(data_object, Experiment):
            """Add an experiment dict to db."""
            return self._database.add(data_object.to_dict())
        elif isinstance(data_object, MultiStageExperiment):
            multistage_dict = data_object.to_dict()
            for step, exp in data_object:
                _id = self._database.add(exp.to_dict())
                step_index = data_object.step_index(step)
                multistage_dict['experiments'][step_index] = (step, _id)
            return self._database.add(multistage_dict)
        # if isinstance(experiment, (Experiment, multistage)):
        #     return self._database.add(experiment)
        else:
            raise TypeError("experiment {} was not Experiment|multistage".format(type(data_object)))

    def get(self, doc_id: int, doc_type: str) -> dict:  # type (int) -> dict
        """Return a experiment dict with matching id."""
        doc = self._database.get(doc_id, doc_type)
        if doc["type"] == "multistage":
            for index, (step, exp_id) in enumerate(doc["experiments"]):
                exp = self._database.get(exp_id, "experiments")
                doc["experiments"][index]= (step, exp)
        return doc

    def list_experiments(self, query: ExperimentQuery = None):  # type (str) -> list[dict]
        """Return list of experiments."""
        return self._database.list_experiments(query=query)

    def count(self) -> int:  # type () -> int
        """Return number of experiments in db."""
        return self._database.count()

    def update(self, experiment_id: int, experiment: Experiment) -> None:
        """Modify experiment in db with given experiment_id."""
        return self._database.update(experiment_id, experiment.to_dict())

    def update_std(self, experiment_id, string, std_type):
        """Update the std tag with new data"""
        if std_type in ['stdout', 'stderr']:
            self._database.update_key(experiment_id, string, std_type, mode='add')
        else:
            raise ValueError("std_type was not stdout or stderr")

    def update_status(self, experiment_id: int, status: str):
        "udpate the status of the experiment"
        if status in ['created', 'running', 'completed', 'error', 'interrupted']:
            self._database.update_key(experiment_id, status, "status", mode='set')
        else:
            raise ValueError("status: {} not correct".format(status))

    def update_monitored(self, experiment_id, key, value):
        exp = self._database.get(experiment_id)
        if key not in exp['monitored']:
            self._database.update_key(experiment_id, value=[value], key=['monitored', key], mode='set')
        else:
            self._database.update_key(experiment_id, value=[value], key=['monitored', key], mode='add')

    def delete(self, experiment_id):  # type (int) -> ()
        """Remove a experiment from db with given experiment_id."""
        self._database.delete(experiment_id)

    def delete_all(self):
        """Remove all experiments from db."""
        self._database.delete_all()

    def stop_db(self):
        """Disconnect from DB."""
        self._database.stop_db()


@contextmanager
def setup_database():
    config_path = os.path.join(os.getcwd(), ".jikken", "config")
    _database = None
    try:
        config = get_config(config_path)
        print(config)
        _database = DataBase(config)
        yield _database
    finally:
        _database.stop_db()
        _database = None
