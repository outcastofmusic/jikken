from typing import Any

from elasticsearch import Elasticsearch, ConnectionError, NotFoundError

from .database import ExperimentQuery, MultiStageExperimentQuery

# from .helpers import add_mongo, map_experiment, inv_map_experiment, set_mongo
from .db_abc import DB, ExperimentType


def create_es_exp_query(query: ExperimentQuery):
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


def create_es_mse_query(query: MultiStageExperimentQuery):
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


class ElasticSearchDB(DB):
    """Wrapper class for MongoDB.
    """

    def __init__(self, db_path: str, db_name: str):
        self._client = None
        self._db = self._connect(db_path)
        self.index = db_name

    def get_index(self, collection: str = "experiment"):
        """ES 6.0 doesn't handle multiple types in the same index so creating one index per type"""
        return self.index + "_" + collection

    def _connect(self, db_path):
        for index in range(3):
            try:
                self._client = Elasticsearch(db_path)
            except ConnectionError:
                index += 1
        return self._client

    def stop_db(self):
        """Disconnect from DB."""
        self._client = None

    def add(self, doc: dict):
        result = self._db.index(index=self.get_index(doc['type']), doc_type=doc['type'], body=doc)
        _id = result["_id"]
        return str(_id)

    def count(self) -> int:
        result = self._db.count()
        return result['count']
        # count = 0
        # for collection in self._db.collection_names(include_system_collections=False):
        #     count += self._db[collection].count()

    def delete(self, experiment_id: int):
        try:
            result = self._db.delete(index=self.get_index("experiment"), doc_type="experiment", id=experiment_id)
        except NotFoundError:
            raise KeyError("experiment id {} not found".format(experiment_id))

    def delete_all(self) -> None:
        """Remove all experiments from db"""
        for index in self._db.indices.get(self.index + '*').keys():
            self._db.indices.delete(index=index)

    def get(self, _id: str, collection: str = "experiments") -> (dict, None):
        """Get a document from the database or None if document not found"""
        res = self._db.get(index=self.get_index(collection), doc_type=collection, id=_id)
        doc = res['_source']
        doc['id'] = res['_id']
        return doc

    def list_experiments(self, query: ExperimentQuery) -> list:
        pass
        # """return a list of experiments that match the query"""
        # if query.is_empty():
        #     return [inv_map_experiment(i) for i in self._db.experiments.find()]
        # elif len(query.ids) > 0:
        #     return [self.get(_id) for _id in query.ids]
        # else:
        #     if len(query.names) > 0:
        #         self._db.experiments.create_index([("name", pymongo.TEXT)], name="search_index", default_language='english')
        #     complex_query = create_mongodb_exp_query(query=query)
        #     return [inv_map_experiment(i) for i in self._db.experiments.find(complex_query)]

    def list_ms_experiments(self, query: MultiStageExperimentQuery) -> list:
        pass
        # if query.is_empty():
        #     return [i for i in self._db["ms_experiments"].find()]
        # elif len(query.ids) > 0:
        #     return [self.get(_id, collection="ms_experiments") for _id in query.ids]
        # else:
        # if len(query.names) > 0:
        #     self._db.ms_experiments.create_index([("name", pymongo.TEXT)], name="search_index", default_language='english')
        # complex_query = create_mongodb_mse_query(query=query)
        # return [i for i in self._db.ms_experiments.find(complex_query)]

    def update(self, experiment_id: int, experiment: dict):
        pass

    def update_key(self, experiment_id: int, value: Any, key: str, mode='set') -> None:
        pass
        # if mode == 'set':
        #     self._db.experiments.update({"_id": ObjectId(experiment_id)}, set_mongo(value, key=key))
        # elif mode == 'add':
        #     self._db.experiments.update({"_id": ObjectId(experiment_id)}, add_mongo(value, key=key))

    @property
    def collections(self) -> list:
        mapping = self._db.indices.get_mapping()
        collections = []
        for index in mapping.keys():
            collections.extend(mapping[index]['mappings'].keys())
        return collections
