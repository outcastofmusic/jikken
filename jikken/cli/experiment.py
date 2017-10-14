import contextlib
import json
import functools
import click
import os
import yaml


def experiment(experiment_filepath=None):
    def experiment_decorator(func):
        @functools.wraps(func)
        def setup_experiment(*args, **kwargs):
            variables = {}
            if experiment_filepath is not None:
                with open(experiment_filepath, 'rt') as file_handle:
                    if experiment_filepath.endswith("json"):
                        variables = json.load(file_handle)
                    elif experiment_filepath.endswith("yaml"):
                        variables = yaml.load(file_handle)
                    else:
                        raise IOError("only json and yaml files are supported")
            kwargs = {**kwargs, **variables}
            return func(*args, **kwargs)

        return setup_experiment

    return experiment_decorator
