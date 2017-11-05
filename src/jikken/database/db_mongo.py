from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
import pymongo
from .database import ExperimentQuery
from pymongo.errors import ConnectionFailure
import time
from .helpers import add_mongo, map_experiment, inv_map_experiment, set_mongo
from .db_abc import DB


class MongoDB(DB):
    """Wrapper class for MongoDB.
    """

    def __init__(self, db_path):
        self._client = None
        self._db = self._connect(db_path)

    def _connect(self, db_path):
        for index in range(3):
            try:
                self._client = pymongo.MongoClient(db_path)
            except ConnectionFailure:
                time.sleep(3)
                index += 1
        return self._client.jikken_db if self._client else None

    def stop_db(self):
        """Disconnect from DB."""
        self._client = None

    def add(self, experiment: dict) -> str:
        exp_db = self._db.experiments
        experiment = map_experiment(experiment)
        exp_id = exp_db.insert_one(experiment).inserted_id
        return str(exp_id)

    def count(self) -> int:
        exp_db = self._db.experiments
        return exp_db.count()

    def delete(self, experiment_id: int):
        try:
            self._db.experiments.delete_one({"_id": ObjectId(experiment_id)})
        except InvalidId:
            raise KeyError("experiment id {} not found".format(experiment_id))

    def delete_all(self) -> None:
        """Remove all experiments from db"""
        self._db.experiments.drop()

    def get(self, experiment_id: str):
        return inv_map_experiment(self._db.experiments.find_one({"_id": ObjectId(experiment_id)}))

    def list_experiments(self, query: ExperimentQuery = None):

        if query is None:
            return [inv_map_experiment(i) for i in self._db.experiments.find()]
        elif query.ids is not None:
            return [self.get(_id) for _id in query.ids]
        else:
            query_list = []
            qt = "$all" if query.query_type == 'and' else "$in"
            if query.tags is not None:
                query_list.append({"tags": {qt: query.tags}})
            if query.schema_param_hashes is not None:
                query_list.append({"parameter_hash": {"$in": query.schema_param_hashes}})
            if query.schema_hashes is not None:
                query_list.append({"schema_hash": {"$in": query.schema_hashes}})
            complex_query = query_list[0] if len(query_list) == 1 else {"$and": query_list}
            return [inv_map_experiment(i) for i in self._db.experiments.find(complex_query)]

    def update(self, experiment_id: int, experiment: dict):
        pass

    def update_key(self, experiment_id: int, value: Any, key: str, mode='set'):
        if mode == 'set':
            self._db.experiments.update({"_id": ObjectId(experiment_id)}, set_mongo(value, key=key))
        elif mode == 'add':
            self._db.experiments.update({"_id": ObjectId(experiment_id)}, add_mongo(value, key=key))