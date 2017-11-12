from functools import reduce
import tinydb
from .database import ExperimentQuery
from traitlets import Any

from jikken import Experiment, MultiStageExperiment
from .helpers import set_inner, add_inner
from tinydb.operations import add, set
from .db_abc import DB


class TinyDB(DB):  # noqa : E801
    """Wrapper class for TinyDB.

    The methods in this class need to match
    all database interaction classes.

    """

    def __init__(self, db_path: str, db_name: str):
        """Connect to db."""
        db = tinydb.TinyDB(db_path + '/jikken_db.json')
        self._db = db.table(db_name)

    def stop_db(self):
        """Disconnect from DB."""
        pass

    def add(self, doc: dict) -> str:
        _id = self._db.insert(doc)
        doc['id'] = str(_id)
        self._db.update(doc, eids=[_id])
        return str(_id)

    def get(self, doc_id: str, collection: str) -> int:
        """Return a experiment dict with matching id."""
        return self._db.get(eid=int(doc_id))

    def list_experiments(self, query: ExperimentQuery = None) -> list:
        """Return list of experiments."""
        if query is None:
            return self._db.all()
        elif query.ids is not None:
            return [self.get(_id) for _id in query.ids]
        else:
            eq = tinydb.Query()
            query_list = []
            if query.tags is not None and len(query.tags) > 0:
                if query.query_type == "and":
                    query_list.append(eq.tags.all(query.tags))
                else:
                    query_list.append(eq.tags.any(query.tags))
            if query.schema_hashes is not None and len(query.schema_hashes) > 0:
                pattern = "(" + ")|(".join(query.schema_hashes) + ")"
                query_list.append(eq.schema_hash.matches(pattern))
            if query.schema_param_hashes is not None and len(query.schema_param_hashes) > 0:
                pattern = "(" + ")|(".join(query.schema_param_hashes) + ")"
                query_list.append(eq.parameter_hash.matches(pattern))
            if query.status is not None and len(query.status) > 0:
                pattern = "(" + ")|(".join(query.status) + ")"
                query_list.append(eq.status.matches(pattern))
            and_query = reduce(lambda x, y: (x) & (y), query_list)
            return self._db.search(and_query)

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

    @property
    def collections(self):
        return ["experiments", "ms_experiments"]