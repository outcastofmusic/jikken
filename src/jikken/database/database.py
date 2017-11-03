from contextlib import contextmanager

from jikken.experiment import Experiment

from .config import get_config


class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super(Singleton, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super(Singleton, self).__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class DataBase(metaclass=Singleton):
    def __init__(self, db_path, db_type):
        if db_type == 'tiny':
            import database.db_tinydb
            self._database = database.db_tinydb.TinyDB.start_db(db_path)
        elif db_type == 'mongo':
            raise NotImplementedError('mongo not implemented yet')
            # import tasks.tasksdb_pymongo
            # _tasksdb = tasks.tasksdb_pymongo.start_tasks_db(db_path)
        else:
            raise ValueError("db_type must be a 'tiny' or 'mongo'")

    def add(self, experiment: Experiment) -> int:
        if isinstance(experiment, Experiment):
            return self._database.add(experiment.to_dict())
        else:
            raise TypeError("experiment {} was not Experiment".format(type(experiment)))

    def get(self, experiment_id: int) -> dict:  # type (int) -> dict
        """Return a experiment dict with matching id."""
        return self._database.get(experiment_id)

    def list_experiments(self, tags=None, query_type="and"):  # type (str) -> list[dict]
        """Return list of experiments."""
        return self._database.list_experiments(tags, query_type)

    def count(self) -> int:  # type () -> int
        """Return number of experiments in db."""
        return self._database.count()

    def update(self, experiment_id, experiment):  # type (int, dict) -> ()
        """Modify experiment in db with given experiment_id."""
        return self._database.update(experiment_id, experiment)

    def update_std(self, experiment_id, string, std_type):
        """Update the std tag with new data"""
        if std_type in ['stdout', 'stderr']:
            self._database.update_key(experiment_id, string, std_type, mode='add')
        else:
            raise ValueError("std_type was not stdout or stderr")

    def delete(self, experiment_id):  # type (int) -> ()
        """Remove a experiment from db with given experiment_id."""
        self._database.delete(experiment_id)

    def delete_all(self):
        """Remove all experiments from db."""
        self._database.delete_all()

    def unique_id(self):  # type () -> int
        """Return an integer that does not exist in the db."""
        return self._database.unique_id()

    def stop_db(self):
        """Disconnect from DB."""
        self._database.stop_db()


@contextmanager
def setup_database():
    _database = None
    try:
        config = get_config()
        _database = DataBase(db_path=config.db_path, db_type=config.db_type)
        yield _database
    finally:
        _database.stop_db()
        _database = None
