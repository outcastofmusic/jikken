from jikken import cli

@cli.experiment(experiment_filepath="./tests/experiment.yaml")
def main(**kwargs):
    return kwargs
