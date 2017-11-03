import os
from subprocess import PIPE, Popen

from .database import setup_database
from .experiment import Experiment
from .monitor import capture_value
from .utils import load_variables_from_filepath


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
    extra_kwargs = [x for argument in args for x in argument]
    extra_vars = {argument[0]: argument[1] for argument in args}
    variables = {**variables, **extra_vars}
    exp = Experiment(variables=variables, code_dir=os.path.dirname(script_path), tags=tags)
    with setup_database() as db:
        exp_id = db.add(exp)
        if script_path.endswith(".py"):
            cmd = ["python3", script_path, "-c", configuration_path] + extra_kwargs
        elif script_path.endswith(".sh"):
            cmd = ["bash", script_path, configuration_path] + extra_kwargs
        error_found = False
        try:
            with Popen(cmd, stderr=PIPE, stdout=PIPE, bufsize=1) as p:
                db.update_status(exp_id, 'running')
                for line in p.stdout:
                    print_out = line.decode('utf-8')
                    db.update_std(exp_id, print_out, std_type='stdout')
                    print(print_out)
                for line in p.stderr:
                    print_out = line.decode('utf-8')

                    monitored = capture_value(print_out)
                    if monitored is not None:
                        db.update_monitored(exp_id, monitored[0], monitored[1])
                    else:
                        db.update_std(exp_id, print_out, std_type='stderr')
                        print(print_out)
                    if 'Error' in print_out:
                        error_found = True
                        db.update_status(exp_id, 'error')
                        print("Experiment Failed")
        except KeyboardInterrupt:
            db.update_status(exp_id, 'interrupted')
            print("Experiment Interrupted")
            error_found = True
        finally:
            if not error_found:
                db.update_status(exp_id, 'completed')
                print("Experiment Done")


def get(_id: int):
    with setup_database() as db:
        experiment = db.get(_id)
    return experiment


def list(ids: list, tags: list, query_type: str):
    with setup_database() as db:
        ids = None if len(ids) == 0 else ids
        tags = None if len(tags) == 0 else tags
        results = db.list_experiments(ids=ids, tags=tags, query_type=query_type)
    return results


def update():
    pass


def delete(_id: int):
    with setup_database() as db:
        db.delete(_id)


def count():
    with setup_database() as db:
        count = db.count()
    return count


def delete_all():
    with setup_database() as db:
        db.delete_all()


def get_best():
    pass


def resume():
    pass
