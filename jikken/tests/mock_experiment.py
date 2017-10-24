import argparse
import json
import os

import click
import yaml

from jikken import cli


@cli.experiment(experiment_definition_filepath="./tests/experiment.yaml")
def main_yaml(**kwargs):
    return kwargs


@cli.experiment(experiment_definition_filepath="./tests/experiment.json")
def main_json(**kwargs):
    return kwargs


@cli.experiment(experiment_definition_filepath="./tests/experiment")
def main_error(**kwargs):
    return kwargs


@cli.cli_experiment
def main_cli(**kwargs):
    click.echo(json.dumps(kwargs))
    return kwargs


if __name__ == '__main__':
    main_cli()
