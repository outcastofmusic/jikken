import functools
from functools import partial
import json
import click
from .utils import load_experiment_from_file, get_code_commit_id, get_schema, get_hash
from types import MappingProxyType
import os


class Experiment:
    def __init__(self, variables, code_directory, tags=None):
        self._variables = variables
        self.commit_id = get_code_commit_id(code_directory)
        self.schema = get_schema(variables)
        self.parameters_schema = get_schema(variables, parameters=True)
        self._schema_hash = ''
        self._parameters_schema_hash = ''
        self.tags = tags

    @property
    def variables(self):
        return MappingProxyType(self._variables)

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

    def __repr__(self):
        return json.dumps(self._variables)


def experiment(func=None, *, experiment_definition_filepath=None):
    if func is None:
        return partial(experiment, experiment_definition_filepath=experiment_definition_filepath)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        variables = load_experiment_from_file(
            experiment_definition_filepath) if experiment_definition_filepath is not None else {}
        exp = Experiment(variables=variables, code_directory=os.getcwd())
        kwargs = {**kwargs, **variables}
        return func(*args, **kwargs)

    return wrapper


def cli_experiment(func=None, *, experiment_definition_filepath=None):
    if func is None:
        return partial(cli_experiment, experiment_definition_filepath=experiment_definition_filepath)

    @click.command()
    @click.argument('experiment_definition', type=click.Path(exists=True))
    @click.argument('tags', nargs=-1)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        variables = load_experiment_from_file(kwargs.pop('experiment_definition'))
        exp = Experiment(variables=variables, code_directory=os.getcwd(), tags=kwargs.pop("tags"))
        kwargs = {**kwargs, **variables}
        return func(*args, **kwargs)

    return wrapper
