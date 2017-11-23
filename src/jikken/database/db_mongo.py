from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
import pymongo

from .database import ExperimentQuery, MultiStageExperimentQuery
from pymongo.errors import ConnectionFailure

from .helpers import add_mongo, map_experiment, inv_map_experiment, set_mongo
from .db_abc import DB


def create_mongodb_exp_query(query: ExperimentQuery):
    """Create a complex mongodb query from an ExperimentQuery Object"""
    query_list = []
    qt = "$all" if query.query_type == 'and' else "$in"
    if len(query.names) > 0:
        name_query = {"$text": {"$search": ' '.join([name for name in query.names])}}
        query_list.append(name_query)
    if len(query.tags) > 0:
        query_list.append({"tags": {qt: query.tags}})
    if len(query.schema_param_hashes) > 0:
        query_list.append({"parameter_hash": {"$in": query.schema_param_hashes}})
    if len(query.schema_hashes) > 0:
        query_list.append({"schema_hash": {"$in": query.schema_hashes}})
    if len(query.status) > 0:
        query_list.append({"status": {"$in": query.status}})
    complex_query = query_list[0] if len(query_list) == 1 else {"$and": query_list}
    return complex_query


def create_mongodb_mse_query(query: MultiStageExperimentQuery):
    """Create a complex mongodb query from an MultiStageExperimentQuery Object"""
    query_list = []
    qt = "$all" if query.query_type == 'and' else "$in"
    if len(query.names) > 0:
        name_query = {"$text": {"$search": ' '.join([name for name in query.names])}}
        query_list.append(name_query)
    if len(query.tags) > 0:
        query_list.append({"tags": {qt: query.tags}})
    if len(query.hashes) > 0:
        query_list.append({"hash": {"$in": query.hashes}})
    if len(query.steps) > 0:
        query_list.append({"steps": {qt: query.steps}})
    complex_query = query_list[0] if len(query_list) == 1 else {"$and": query_list}
    return complex_query

class MongoDB(DB):
    """Wrapper class for MongoDB.
    """

    def __init__(self, db_path: str, db_name: str):
        self._client = None
        self._db = self._connect(db_path, db_name)
        for collection in self.collections:
            self._db[collection].create_index([("name", pymongo.TEXT)], name="search_index", default_language='english')

    def _connect(self, db_path, db_name):
        for index in range(3):
            try:
                self._client = pymongo.MongoClient(db_path)
                _ = self._client.database_names()
            except ConnectionFailure:
                index += 1
        return self._client[db_name] if self._client else None

    def stop_db(self):
        """Disconnect from DB."""
        self._client = None

    def add(self, doc: dict):
        if doc["type"] == "experiment":
            doc = map_experiment(doc)
            col = self._db[doc['type']]
        else:
            col = self._db[doc["type"]]
        _id = col.insert_one(doc).inserted_id
        return str(_id)

    def count(self) -> int:
        count = 0
        for collection in self._db.collection_names(include_system_collections=False):
            count += self._db[collection].count()
        return count

    def delete(self, experiment_id: int):
        try:
            self._db.experiment.delete_one({"_id": ObjectId(experiment_id)})
        except InvalidId:
            raise KeyError("experiment id {} not found".format(experiment_id))

    def delete_all(self) -> None:
        """Remove all experiments from db"""
        for collection in self._db.collection_names(include_system_collections=False):
            self._db[collection].drop()

    def get(self, _id: str, collection: str = "experiment") -> (dict, None):
        """Get a document from the database or None if document not found"""
        doc = self._db[collection].find_one({"_id": ObjectId(_id)})
        if doc is None:
            return
        elif doc["type"] == "experiment":
            return inv_map_experiment(doc)
        else:
            doc['id'] = doc.pop('_id')
            return doc

    def list_experiments(self, query: ExperimentQuery) -> list:
        """return a list of experiments that match the query"""
        if query.is_empty():
            return [inv_map_experiment(i) for i in self._db.experiment.find()]
        elif len(query.ids) > 0:
            return [self.get(_id) for _id in query.ids]
        else:
            if len(query.names) > 0:
                self._db.experiment.create_index([("name", pymongo.TEXT)], name="search_index", default_language='english')
            complex_query = create_mongodb_exp_query(query=query)
            return [inv_map_experiment(i) for i in self._db.experiment.find(complex_query)]

    def list_ms_experiments(self, query: MultiStageExperimentQuery)-> list:
        if query.is_empty():
            return [i for i in self._db["multistage"].find()]
        elif len(query.ids) > 0:
            return [self.get(_id, collection="multistage") for _id in query.ids]
        else:
            if len(query.names) > 0:
                self._db.multistage.create_index([("name", pymongo.TEXT)], name="search_index", default_language='english')
            complex_query = create_mongodb_mse_query(query=query)
            return [i for i in self._db.multistage.find(complex_query)]

    def update(self, experiment_id: int, experiment: dict):
        pass

    def update_key(self, experiment_id: int, value: Any, key: str, mode='set') -> None:
        if mode == 'set':
            self._db.experiment.update({"_id": ObjectId(experiment_id)}, set_mongo(value, key=key))
        elif mode == 'add':
            self._db.experiment.update({"_id": ObjectId(experiment_id)}, add_mongo(value, key=key))

