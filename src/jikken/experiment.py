import json
from types import MappingProxyType

from .utils import get_commit_id, get_commit_status, get_hash, get_repo_origin, get_schema


class Experiment:
    def __init__(self, variables: dict, code_dir: str, tags: list = None):
        """The Experiment object encapsulates a possible experiment

        Args:
            variables (dict): A  possibly nested dictionary with all variables that define the experiment
            code_dir (str): A github directory that holds the code to be run
            tags (list, None): An optional list of tags that describe the experiment
        """
        self._variables = variables
        self.commit_id = get_commit_id(code_dir)
        self.git_repo_origin = get_repo_origin(code_dir)
        self.commit_status = get_commit_status(code_dir)
        self.schema = get_schema(variables)
        self.parameters_schema = get_schema(variables, parameters=True)
        self._schema_hash = ''
        self._parameters_schema_hash = ''
        self._tags = tags

    @property
    def variables(self):
        return MappingProxyType(self._variables)

    @property
    def tags(self):
        return self._tags

    @property
    def schema_hash(self):
        if self._schema_hash == '':
            self._schema_hash = get_hash(self.schema)
        return self._schema_hash

    @property
    def parameters_hash(self):
        if self._parameters_schema_hash == '':
            self._parameters_schema_hash = get_hash(self.parameters_schema)
        return self._parameters_schema_hash

    @property
    def hash(self):
        return self.parameters_hash

    def __repr__(self):
        return json.dumps(self._variables)

    def to_dict(self):
        return {
            "variables": self._variables,
            "commit_id": self.commit_id,
            "dirty": self.commit_status,
            "repo": self.git_repo_origin,
            "tags": self.tags,
            "parameter_hash": self.parameters_hash,
            "schema_hash": self.schema_hash,
            "id": None,
            "stdout": "",
            "stderr": "",
            "status": "created",
            "monitored": {}
        }
