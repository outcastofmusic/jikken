from typing import Any

import pymongo
from pymongo.errors import ConnectionFailure
import time
from .db_abc import DB


def replace_dots(experiment: dict):
    new_experiment = {}
    for key in experiment['variables'].keys():
        new_key = key.replace(".", "__")
        new_experiment[new_key] = experiment['variables'][key]
    experiment['variables'] = new_experiment
    return experiment


def fix_experiment(experiment: dict):
    new_experiment = {}
    for key in experiment['variables'].keys():
        new_key = key.replace("__", ".")
        new_experiment[new_key] = experiment['variables'][key]
    experiment['variables'] = new_experiment
    experiment['id'] = str(experiment.pop("_id"))
    return experiment


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
        experiment = replace_dots(experiment)
        exp_id = exp_db.insert_one(experiment).inserted_id
        return str(exp_id)

    def count(self) -> int:
        exp_db = self._db.experiments
        return exp_db.count()

    def delete(self, experiment_id: int):
        pass

    def delete_all(self) -> None:
        """Remove all experiments from db"""
        self._db.experiments.drop()

    def get(self, experiment_id: int):
        pass

    def list_experiments(self, ids: list = None, tags: list = None, query_type: str = "and"):
        if tags is None and ids is None:
            return [fix_experiment(i) for i in self._db.experiments.find()]
        elif ids is not None:
            return [self.get(_id) for _id in ids]
        elif query_type == "and":
            return self._db.search(tinydb.Query().tags.all(tags))
        elif query_type == "or":
            return self._db.search(tinydb.Query().tags.any(tags))

    def update(self, experiment_id: int, experiment: dict):
        pass

    def update_key(self, experiment_id: int, value: Any, key: str, mode='set'):
        pass
