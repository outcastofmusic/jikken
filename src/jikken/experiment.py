import json
from types import MappingProxyType

from .utils import get_code_commit_id, get_schema, get_hash


class Experiment:
    def __init__(self, variables: dict, code_dir: str, tags: list = None):
        """The Experiment object encapsulates a possible experiment

        Args:
            variables (dict): A  possibly nested dictionary with all variables that define the experiment
            code_dir (str): A github directory that holds the code to be run
            tags (list, None): An optional list of tags that describe the experiment
        """
        self._variables = variables
        self.commit_id = get_code_commit_id(code_dir)
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
    def experiment_schema_hash(self):
        if self._schema_hash == '':
            self._schema_hash = get_hash(self.schema)
        return self._schema_hash

    @property
    def experiment_parameters_hash(self):
        if self._parameters_schema_hash == '':
            self._parameters_schema_hash = get_hash(self.parameters_schema)
        return self._parameters_schema_hash

    @property
    def hash(self):
        return self.experiment_parameters_hash + self.commit_id

    def __repr__(self):
        return json.dumps(self._variables)
