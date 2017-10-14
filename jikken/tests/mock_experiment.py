from jikken import cli

@cli.experiment(experiment_filepath="./tests/experiment.yaml")
def main_yaml(**kwargs):
    return kwargs


@cli.experiment(experiment_filepath="./tests/experiment.json")
def main_json(**kwargs):
    return kwargs

@cli.experiment(experiment_filepath="./tests/experiment")
def main_error(**kwargs):
    return kwargs
