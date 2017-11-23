from functools import reduce
import tinydb
from .database import ExperimentQuery, MultiStageExperimentQuery
from typing import Any
from .helpers import set_inner, add_inner
from tinydb.operations import add, set
from .db_abc import DB


def create_tinydb_exp_query(query: ExperimentQuery):
    """Create a complex query for experiments"""
    eq = tinydb.Query()
    query_list = []
    if len(query.names) > 0:
        query_list.append(eq.name.search(r'(' + r'|'.join(query.names) + r')'))
    if len(query.tags) > 0:
        if query.query_type == "and":
            query_list.append(eq.tags.all(query.tags))
        else:
            query_list.append(eq.tags.any(query.tags))
    if len(query.schema_hashes) > 0:
        pattern = r"(" + r")|(".join(query.schema_hashes) + r")"
        query_list.append(eq.schema_hash.matches(pattern))
    if len(query.schema_param_hashes) > 0:
        pattern = r"(" + r")|(".join(query.schema_param_hashes) + r")"
        query_list.append(eq.parameter_hash.matches(pattern))
    if len(query.status) > 0:
        pattern = r"(" + r")|(".join(query.status) + r")"
        query_list.append(eq.status.matches(pattern))
    and_query = reduce(lambda x, y: (x) & (y), query_list)
    return and_query


def create_tinydb_mse_query(query: MultiStageExperimentQuery):
    """Create a complex query for MultiStage Experiments"""
    eq = tinydb.Query()
    query_list = []
    if len(query.names) > 0:
        query_list.append(eq.name.search(r'(' + r'|'.join(query.names) + r')'))
    if len(query.tags) > 0:
        if query.query_type == "and":
            query_list.append(eq.tags.all(query.tags))
        else:
            query_list.append(eq.tags.any(query.tags))
    if len(query.hashes) > 0:
        pattern = r"(" + r")|(".join(query.schema_hashes) + r")"
        query_list.append(eq.hash.matches(pattern))
    if len(query.steps) > 0:
        if query.query_type == "and":
            query_list.append(eq.steps.all(query.steps))
        else:
            query_list.append(eq.steps.any(query.steps))
    and_query = reduce(lambda x, y: (x) & (y), query_list)
    return and_query


class TinyDB(DB):  # noqa : E801
    """Wrapper class for TinyDB.

    The methods in this class need to match
    all database interaction classes.

    """

    def __init__(self, db_path: str, db_name: str):
        """Connect to db."""
        db = tinydb.TinyDB(db_path + '/jikken_db.json')
        self._db = dict()
        for collection in self.collections:
            self._db[collection] = db.table(db_name + "_" + collection)

    def stop_db(self):
        """Disconnect from DB."""
        pass

    def add(self, doc: dict) -> str:
        _id = self._db[doc["type"]].insert(doc)
        doc['id'] = str(_id)
        self._db[doc["type"]].update(doc, eids=[_id])
        return str(_id)

    def get(self, doc_id: str, collection: str) -> int:
        """Return a experiment dict with matching id."""
        return self._db[collection].get(eid=int(doc_id))

    def list_experiments(self, query: ExperimentQuery) -> list:
        """Return list of experiments."""
        if query.is_empty():
            return self._db["experiment"].all()
        elif len(query.ids) > 0:
            return [self.get(_id, "experiment") for _id in query.ids]
        else:
            complex_query = create_tinydb_exp_query(query=query)
            return self._db["experiment"].search(complex_query)

    def list_ms_experiments(self, query: MultiStageExperimentQuery) -> None:
        if query.is_empty():
            return self._db["multistage"].all()
        elif len(query.ids) > 0:
            return [self.get(_id, "multistage") for _id in query.ids]
        else:
            complex_query = create_tinydb_mse_query(query=query)
            return self._db["multistage"].search(complex_query)

    def count(self) -> int:
        """Return number of experiments in db."""
        count = sum([len(self._db[collection]) for collection in self.collections])
        return count

    def update(self, experiment_id: str, experiment: dict) -> None:
        """Modify experiment in db with given experiment_id."""
        self._db["experiment"].update(experiment, eids=[int(experiment_id)])

    def update_key(self, experiment_id: str, value: Any, key: (list, str), mode='set') -> None:
        experiment_id = int(experiment_id)
        if mode == 'set' and isinstance(key, list):
            self._db["experiment"].update(set_inner(key, value), eids=[experiment_id])
        elif mode == 'set':
            self._db["experiment"].update(set(key, value), eids=[experiment_id])
        elif mode == 'add' and isinstance(key, list):
            self._db["experiment"].update(add_inner(key, value), eids=[experiment_id])
        elif mode == 'add':
            self._db["experiment"].update(add(key, value), eids=[experiment_id])
        else:
            raise ValueError("update mode {} not supported ".format(mode))

    def delete(self, experiment_id: str) -> None:
        """Remove a experiment from db with given experiment_id."""
        try:
            self._db["experiment"].remove(eids=[int(experiment_id)])
        except ValueError:
            raise KeyError("key {} not found in TinyDB".format(experiment_id))

    def delete_all(self) -> None:
        """Remove all experiments from db."""
        for collection in self.collections:
            self._db[collection].purge()
