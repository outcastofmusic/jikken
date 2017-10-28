import json

import click

from jikken import experiment


@experiment.experiment(experiment_definition_filepath="./tests/experiment.yaml")
def main_yaml(**kwargs):
    return kwargs


@experiment.experiment(experiment_definition_filepath="./tests/experiment.json")
def main_json(**kwargs):
    return kwargs


@experiment.experiment(experiment_definition_filepath="./tests/experiment")
def main_error(**kwargs):
    return kwargs


@experiment.cli_experiment
def main_cli(**kwargs):
    click.echo(json.dumps(kwargs))
    return kwargs


if __name__ == '__main__':
    main_cli()
