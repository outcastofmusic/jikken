from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
import pymongo

from .database import ExperimentQuery
from pymongo.errors import ConnectionFailure

from jikken import Experiment, Pipeline
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

    def _add(self, data_object: dict, collection: str):
        col = self._db[collection]
        _id = col.insert_one(data_object).inserted_id
        return str(_id)

    def add(self, data_object: (Experiment, Pipeline)) -> str:
        if isinstance(data_object, Experiment):
            data_object = map_experiment(data_object.to_dict())
            return self._add(data_object, "experiments")
        elif isinstance(data_object, Pipeline):
            pipeline_dict = data_object.to_dict()
            for step, exp in data_object:
                exp_dict = map_experiment(exp.to_dict())
                _id = self._add(exp_dict, "experiments")
                step_index = data_object.step_index(step)
                pipeline_dict['experiments'][step_index] = _id
            return self._add(pipeline_dict, "pipelines")

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
