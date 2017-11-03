import tinydb
from tinydb.operations import add, set


def add_inner(fields, n):
    """
    Add n to a given field in the document.
    """

    def transform(doc):
        for field in fields[:-1]:
            ref = doc[field]
        ref[fields[-1]] += n

    return transform


def set_inner(fields, n):
    """
    Set n from a given field in the document.
    """

    def transform(doc):
        for field in fields[:-1]:
            ref = doc[field]
        ref[fields[-1]] = n

    return transform


class TinyDB:  # noqa : E801
    """Wrapper class for TinyDB.

    The methods in this class need to match
    all database interaction classes.

    """

    @classmethod
    def start_db(cls, db_path):
        return cls(db_path)

    def __init__(self, db_path):  # type (str) -> ()
        """Connect to db."""
        self._db = tinydb.TinyDB(db_path + '/jikken_db.json')

    def add(self, experiment):  # type (dict) -> int
        """Add an experiment dict to db."""
        experiment_id = self._db.insert(experiment)
        experiment['id'] = experiment_id
        self._db.update(experiment, eids=[experiment_id])
        return experiment_id

    def get(self, experiment_id):  # type (int) -> dict
        """Return a experiment dict with matching id."""
        return self._db.get(eid=experiment_id)

    def list_experiments(self, ids=None, tags=None, query_type="and"):  # type (str) -> list[dict]
        """Return list of experiments."""
        if tags is None and ids is None:
            return self._db.all()
        elif ids is not None:
            return [self.get(_id) for _id in ids]
        elif query_type == "and":
            return self._db.search(tinydb.Query().tags.all(tags))
        elif query_type == "or":
            return self._db.search(tinydb.Query().tags.any(tags))

    def count(self):  # type () -> int
        """Return number of experiments in db."""
        return len(self._db)

    def update(self, experiment_id, experiment):  # type (int, dict) -> ()
        """Modify experiment in db with given experiment_id."""
        self._db.update(experiment, eids=[experiment_id])

    def update_key(self, experiment_id, value, key, mode='set'):
        if mode == 'set' and isinstance(key, list):
            self._db.update(set_inner(key, value), eids=[experiment_id])
        elif mode == 'set':
            self._db.update(set(key, value), eids=[experiment_id])
        elif mode == 'add' and isinstance(key, list):
            self._db.update(set_inner(key, value), eids=[experiment_id])
        elif mode == 'add':
            self._db.update(add(key, value), eids=[experiment_id])
        else:
            raise ValueError("update mode {} not supported ".format(mode))

    def delete(self, experiment_id):  # type (int) -> ()
        """Remove a experiment from db with given experiment_id."""
        self._db.remove(eids=[experiment_id])

    def delete_all(self):
        """Remove all experiments from db."""
        self._db.purge()

    def unique_id(self):  # type () -> int
        """Return an integer that does not exist in the db."""
        i = 1
        while self._db.contains(eids=[i]):
            i += 1
        return i

    def stop_db(self):
        """Disconnect from DB."""
        pass
