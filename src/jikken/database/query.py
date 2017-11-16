def valid_list(value=None):
    assert value is None or isinstance(value, (tuple, list)), "value: {} is not a list or None".format(value)
    if value is None:
        return []
    else:
        return list(value)


class ExperimentQuery:
    def __init__(self, tags=None, ids=None, schema_hashes=None, status=None, schema_param_hashes=None, names=None,
                 query_type="all"):
        self._tags = valid_list(tags)
        self._ids = valid_list(ids)
        self._schema_hashes = valid_list(schema_hashes)
        self._schema_param_hashes = valid_list(schema_param_hashes)
        self._status = valid_list(status)
        self._names = valid_list(names)
        assert query_type in ["all", "any"], "query type {} is not valid".format(query_type)
        self._query_type = "and" if query_type == "all" else "or"

    @property
    def tags(self):
        return self._tags

    @property
    def ids(self):
        return self._ids

    @property
    def schema_hashes(self):
        return self._schema_hashes

    @property
    def schema_param_hashes(self):
        return self._schema_param_hashes

    @property
    def names(self):
        return self._names

    @property
    def query_type(self):
        return self._query_type

    @property
    def status(self):
        return self._status

    def is_empty(self):
        return len(self.tags) == len(self.names) == len(self.schema_hashes) == len(self.schema_param_hashes) == len(
            self.ids) == 0
    def __repr__(self):
        return "ids: {}\ntags: {}\nnames: {}\nschema_hashes: {}\nschema_param_hashes {}\nstatus:{}\nquery_type: {}".format(
            self.ids, self.tags, self.names, self.schema_hashes, self.schema_param_hashes, self.status, self.query_type
        )

class MultiStageExperimentQuery:
    def __init__(self, tags=None, ids=None, names=None, steps=None, hashes=None, query_type="all"):
        self._tags = valid_list(tags)
        self._ids = valid_list(ids)
        self._hashes = valid_list(hashes)
        self._steps = valid_list(steps)
        self._names = valid_list(names)
        assert query_type in ["all", "any"], "query type {} is not valid".format(query_type)
        self._query_type = "and" if query_type == "all" else "or"

    @property
    def tags(self):
        return self._tags

    @property
    def ids(self):
        return self._ids

    @property
    def hashes(self):
        return self._hashes

    @property
    def steps(self):
        return self._steps

    @property
    def names(self):
        return self._names

    @property
    def query_type(self):
        return self._query_type

    def is_empty(self):
        return len(self.tags) == len(self.names) == len(self.hashes) == len(self.steps) == len(
            self.ids) == 0

    def __repr__(self):
        return "ids: {}\ntags: {}\nnames: {}\nhashes: {}\nsteps {}\nquery_type: {}".format(
            self.ids, self.tags, self.names, self.hashes, self.steps, self.query_type
        )
