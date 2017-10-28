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

# def experiment(func=None, *, experiment_definition_filepath=None):
#     if func is None:
#         return partial(experiment, experiment_definition_filepath=experiment_definition_filepath)
#
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         variables = load_experiment_from_filepath(
#             experiment_definition_filepath) if experiment_definition_filepath is not None else {}
#         exp = Experiment(variables=variables, code_directory=os.getcwd())
#         kwargs = {**kwargs, **variables}
#         f = io.StringIO()
#         with redirect_stdout(f):
#             results = func(*args, **kwargs)
#         print(f.getvalue())
#         return results
#
#     return wrapper
#
#
# def cli_experiment(func=None, *, experiment_definition_filepath=None):
#     if func is None:
#         return partial(cli_experiment, experiment_definition_filepath=experiment_definition_filepath)
#
#     @click.command()
#     @click.argument('experiment_definition', type=click.Path(exists=True, file_okay=True, dir_okay=True))
#     @click.option('--tags', '-t', multiple=True)
#     @click.option('--is_main', is_flag=True)
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         run = kwargs.pop('is_main')
#         experiment_definition = kwargs.pop('experiment_definition')
#         if run:
#             variables = load_experiment_from_filepath(experiment_definition)
#             exp = Experiment(variables=variables, code_directory=os.getcwd(), tags=kwargs.pop("tags"))
#             kwargs = {**kwargs, **variables}
#             return func(*args, **kwargs)
#         else:
#             cmd = ["python3", inspect.getfile(func), experiment_definition, '--is_main']
#             with Popen(cmd, stderr=PIPE, stdout=PIPE, bufsize=1) as p:
#                 for line in p.stdout:
#                     print(line.decode('utf-8'))
#
#     return wrapper
