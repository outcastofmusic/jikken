import os
from subprocess import Popen, PIPE

from .experiment import Experiment
from .utils import load_variables_from_filepath
from .database import setup_database


def run(*, configuration_path, script_path, args=None, tags=None, reference_configuration_path=None):
    """Runs an experiment script and captures the stdout and stderr

    Args:
        configuration_path (str): The path to the configuration file/dir of the experiment
        script_path (str): The path to the script that will run the experiment
        args (list): Optional, list of strings with extra args not included in the configuration_path to
             be passed to the script. Expected form is ["arg1=x", "arg2=y", "arg3=z"]
        tags (list): Optional, list of strings with tags that describe the experiment
        reference_configuration_path (str): Optional a path for a reference configuration. If it is given
            the reference_configuration_path defines the experiment and the configuration_path only requires
            the updated variables
    """
    variables = load_variables_from_filepath(configuration_path)
    args = [] if args is None else [argument.split("=") for argument in args]
    extra_args = [x for argument in args for x in argument]
    extra_vars = {argument[0]: argument[1] for argument in args}
    variables = {**variables, **extra_vars}
    exp = Experiment(variables=variables, code_dir=os.path.dirname(script_path), tags=tags)
    cmd = ["python3", script_path, "-c", configuration_path] + extra_args
    with Popen(cmd, stderr=PIPE, stdout=PIPE, bufsize=1) as p:
        for line in p.stdout:
            print(line.decode('utf-8'))
        for line in p.stderr:
            print(line.decode('utf-8'))


def add(experiment: Experiment):
    if not isinstance(experiment, Experiment):
        raise TypeError("experiment to be added should be an Experiment Object" )
    with setup_database() as db:
        db.add(experiment)


def get():
    pass

def list():
    pass


def update():
    pass


def delete():
    pass


def count():
    pass


def delete_all():
    pass


def get_best():
    pass


def unique_id():
    pass
