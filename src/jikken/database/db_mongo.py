from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
import pymongo

from .database import ExperimentQuery
from pymongo.errors import ConnectionFailure

from jikken import Experiment, MultiStageExperiment
from .helpers import add_mongo, map_experiment, inv_map_experiment, set_mongo
from .db_abc import DB


class MongoDB(DB):
    """Wrapper class for MongoDB.
    """

    def __init__(self, db_path: str, db_name: str):
        self._client = None
        self._db = self._connect(db_path, db_name)

    def _connect(self, db_path, db_name):
        for index in range(3):
            try:
                self._client = pymongo.MongoClient(db_path)
                db_names = self._client.database_names()
            except ConnectionFailure:
                index += 1
        return self._client[db_name] if self._client else None

    def stop_db(self):
        """Disconnect from DB."""
        self._client = None

    def add(self, doc: dict):
        if doc["type"] == "experiment":
            doc = map_experiment(doc)
            col = self._db["experiments"]
        else:
            col = self._db["ms_experiments"]
        _id = col.insert_one(doc).inserted_id
        return str(_id)

    def count(self) -> int:
        count = 0
        for collection in self._db.collection_names(include_system_collections=False):
            count += self._db[collection].count()
        return count

    def delete(self, experiment_id: int):
        try:
            self._db.experiments.delete_one({"_id": ObjectId(experiment_id)})
        except InvalidId:
            raise KeyError("experiment id {} not found".format(experiment_id))

    def delete_all(self) -> None:
        """Remove all experiments from db"""
        for collection in self._db.collection_names(include_system_collections=False):
            self._db[collection].drop()

    def get(self, _id: str, collection: str = "experiments"):
        doc = self._db[collection].find_one({"_id": ObjectId(_id)})
        if doc is None:
            return
        elif doc["type"] == "experiment":
            return inv_map_experiment(doc)
        else:
            doc['id'] = doc.pop('_id')
            return doc

    def list_experiments(self, query: ExperimentQuery = None):

        if query is None:
            return [inv_map_experiment(i) for i in self._db.experiments.find()]
        elif query.ids is not None and len(query.ids) > 0:
            return [self.get(_id) for _id in query.ids]
        else:
            query_list = []
            qt = "$all" if query.query_type == 'and' else "$in"
            if query.tags is not None and len(query.tags) > 0:
                query_list.append({"tags": {qt: query.tags}})
            if query.schema_param_hashes is not None and len(query.schema_param_hashes) > 0:
                query_list.append({"parameter_hash": {"$in": query.schema_param_hashes}})
            if query.schema_hashes is not None and len(query.schema_hashes) > 0:
                query_list.append({"schema_hash": {"$in": query.schema_hashes}})
            if query.status is not None and len(query.status) > 0:
                query_list.append({"status": {"$in": query.status}})
            complex_query = query_list[0] if len(query_list) == 1 else {"$and": query_list}
            return [inv_map_experiment(i) for i in self._db.experiments.find(complex_query)]

    def update(self, experiment_id: int, experiment: dict):
        pass

    def update_key(self, experiment_id: int, value: Any, key: str, mode='set'):
        if mode == 'set':
            self._db.experiments.update({"_id": ObjectId(experiment_id)}, set_mongo(value, key=key))
        elif mode == 'add':
            self._db.experiments.update({"_id": ObjectId(experiment_id)}, add_mongo(value, key=key))

    @property
    def collections(self):
        return self._db.collection_names(include_system_collections=False)
