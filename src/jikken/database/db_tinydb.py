import tinydb
from traitlets import Any

from .helpers import set_inner, add_inner
from tinydb.operations import add, set
from .db_abc import DB


class TinyDB(DB):  # noqa : E801
    """Wrapper class for TinyDB.

    The methods in this class need to match
    all database interaction classes.

    """

    def __init__(self, db_path):  # type (str) -> ()
        """Connect to db."""
        self._db = tinydb.TinyDB(db_path + '/jikken_db.json')

    def stop_db(self):
        """Disconnect from DB."""
        pass

    def add(self, experiment: str) -> int:
        """Add an experiment dict to db."""
        experiment_id = self._db.insert(experiment)
        experiment['id'] = experiment_id
        self._db.update(experiment, eids=[experiment_id])
        return str(experiment_id)

    def get(self, experiment_id: str) -> int:
        """Return a experiment dict with matching id."""
        return self._db.get(eid=int(experiment_id))

    def list_experiments(self, ids=None, tags=None, query_type="and") -> list:
        """Return list of experiments."""
        if tags is None and ids is None:
            return self._db.all()
        elif ids is not None:
            return [self.get(_id) for _id in ids]
        elif query_type == "and":
            return self._db.search(tinydb.Query().tags.all(tags))
        elif query_type == "or":
            return self._db.search(tinydb.Query().tags.any(tags))

    def count(self) -> int:
        """Return number of experiments in db."""
        return len(self._db)

    def update(self, experiment_id: str, experiment: dict) -> None:
        """Modify experiment in db with given experiment_id."""
        self._db.update(experiment, eids=[int(experiment_id)])

    def update_key(self, experiment_id: str, value: Any, key: (list, str), mode='set') -> None:
        experiment_id = int(experiment_id)
        if mode == 'set' and isinstance(key, list):
            self._db.update(set_inner(key, value), eids=[experiment_id])
        elif mode == 'set':
            self._db.update(set(key, value), eids=[experiment_id])
        elif mode == 'add' and isinstance(key, list):
            self._db.update(add_inner(key, value), eids=[experiment_id])
        elif mode == 'add':
            self._db.update(add(key, value), eids=[experiment_id])
        else:
            raise ValueError("update mode {} not supported ".format(mode))

    def delete(self, experiment_id: str) -> None:
        """Remove a experiment from db with given experiment_id."""
        try:
            self._db.remove(eids=[int(experiment_id)])
        except ValueError:
            raise KeyError("key {} not found in TinyDB".format(experiment_id))

    def delete_all(self) -> None:
        """Remove all experiments from db."""
        self._db.purge()
