from typing import Any

from elasticsearch import Elasticsearch, ConnectionError, NotFoundError

from .database import ExperimentQuery, MultiStageExperimentQuery
from .helpers import inv_map_es_experiment, map_es_experiment
from .db_abc import DB


def create_term_query(key, values, query_type):
    """Return an all or any term query for es"""
    if query_type == "or":
        return [{"terms": {key: values}}]
    else:
        return [{"term": {key: value}} for value in values]


def add_filter_query(query_dsl, key, values, query_type="or"):
    """create filter es subqueries for terms"""
    if "filter" not in query_dsl["bool"]:
        query_dsl["bool"]["filter"] = {"bool": {"must": create_term_query(key, values, query_type)}}
    else:
        query_dsl["bool"]["filter"]["bool"]["must"].append(create_term_query(key, values, query_type))
    return query_dsl


def create_es_exp_query(query: ExperimentQuery):
    """Create a complex es query from an ExperimentQuery Object"""
    complex_query = {"bool": {}}

    if len(query.names) > 0:
        name_query = [{"match": {"name": name}} for name in query.names]
        complex_query["bool"]["must"] = [{"bool": {"should": name_query, "minimum_should_match": 1}}]
    if len(query.tags) > 0:
        complex_query = add_filter_query(complex_query, key="tags", values=query.tags, query_type=query.query_type)
    if len(query.schema_param_hashes) > 0:
        complex_query = add_filter_query(complex_query, key="parameter_hash", values=query.schema_param_hashes)
    if len(query.schema_hashes) > 0:
        complex_query = add_filter_query(complex_query, key="schema_has", values=query.schema_hashes)
    if len(query.status) > 0:
        complex_query = add_filter_query(complex_query, key="status", values=query.status)
    complex_query = {"query": complex_query}
    return complex_query


def create_es_mse_query(query: MultiStageExperimentQuery):
    """Create a complex es query from an MultiStageExperimentQuery Object"""
    complex_query = {"bool": {}}

    if len(query.names) > 0:
        name_query = [{"match": {"name": name}} for name in query.names]
        complex_query["bool"]["must"] = [{"bool": {"should": name_query, "minimum_should_match": 1}}]
    if len(query.tags) > 0:
        complex_query = add_filter_query(complex_query, key="tags", values=query.tags, query_type=query.query_type)
    if len(query.hashes) > 0:
        complex_query = add_filter_query(complex_query, key="hash", values=query.hashes)
    if len(query.steps) > 0:
        complex_query = add_filter_query(complex_query, key="steps", values=query.steps, query_type=query.query_type)
    complex_query = {"query": complex_query}
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
        result = self._db.index(index=self.get_index(doc['type']), doc_type=doc['type'],
                                body=map_es_experiment(doc, doc['type']), refresh='wait_for')
        _id = result["_id"]
        return str(_id)

    def count(self) -> int:
        result = self._db.count()
        return result['count']

    def delete(self, experiment_id: int):
        try:
            result = self._db.delete(index=self.get_index("experiment"), doc_type="experiment", id=experiment_id,
                                     refresh='wait_for')
        except NotFoundError:
            raise KeyError("experiment id {} not found".format(experiment_id))

    def delete_all(self) -> None:
        """Remove all experiments from db"""
        for index in self._db.indices.get(self.index + '*').keys():
            self._db.indices.delete(index=index)

    def get(self, _id: str, collection: str = "experiment") -> (dict, None):
        """Get a document from the database or None if document not found"""
        res = self._db.get(index=self.get_index(collection), doc_type=collection, id=_id)
        return inv_map_es_experiment(res, collection)

    def list_experiments(self, query: ExperimentQuery) -> list:
        """return a list of experiments that match the query"""
        if query.is_empty():
            results = self._db.search(index=self.get_index("experiment"))
            return [inv_map_es_experiment(doc) for doc in results['hits']['hits']]
        elif len(query.ids) > 0:
            return [self.get(_id, collection="experiment") for _id in query.ids]
        else:
            complex_query = create_es_exp_query(query=query)
            results = self._db.search(index=self.get_index("experiment"), body=complex_query)
            return [inv_map_es_experiment(doc) for doc in results['hits']['hits']]

    def list_ms_experiments(self, query: MultiStageExperimentQuery) -> list:
        if query.is_empty():
            results = self._db.search(index=self.get_index("multistage"))
            results = [inv_map_es_experiment(doc, "multistage") for doc in results['hits']['hits']]
        elif len(query.ids) > 0:
            results = [self.get(_id, collection="multistage") for _id in query.ids]
        else:
            complex_query = create_es_mse_query(query=query)
            results = self._db.search(index=self.get_index("multistage"), body=complex_query)
            results = [inv_map_es_experiment(doc, "multistage") for doc in results['hits']['hits']]
        return results

    def update(self, experiment_id: int, experiment: dict):
        pass

    def update_key(self, experiment_id: int, value: Any, key: str, mode='set') -> None:
        if mode == "set":
            body = {"doc": {key: value}}
        else:
            body = {
                "script": {
                    "source": "ctx._source.{field}.add(params.value)".format(field=key),
                    "lang": "painless",
                    "params": {
                        "value": value
                    }
                }
            }

        self._db.update(index=self.get_index("experiment"),
                        doc_type="experiment",
                        id=experiment_id,
                        body=body,
                        )

    @property
    def collections(self) -> list:
        mapping = self._db.indices.get_mapping()
        collections = []
        for index in mapping.keys():
            collections.extend(mapping[index]['mappings'].keys())
        return collections
