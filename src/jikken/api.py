import os
from subprocess import PIPE, Popen

from .database import setup_database
from .experiment import Experiment
from .monitor import capture_value
from .utils import load_variables_from_filepath


def run(*, configuration_path: str, script_path: str, args: list = None, tags: list = None,
        reference_configuration_path: str = None) -> None:
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
    # TODO add ability to use reference_configuration_path
    variables = load_variables_from_filepath(configuration_path)
    args = [] if args is None else [argument.split("=") for argument in args]
    extra_kwargs = [x for argument in args for x in argument]
    extra_vars = {argument[0]: argument[1] for argument in args}
    variables = {**variables, **extra_vars}
    # TODO decide if extra_vars can be the same and overwrite the variables or not
    exp = Experiment(variables=variables, code_dir=os.path.dirname(script_path), tags=tags)
    with setup_database() as db:
        exp_id = db.add(exp)
        if script_path.endswith(".py"):
            cmd = ["python3", script_path, "-c", configuration_path] + extra_kwargs
        elif script_path.endswith(".sh"):
            cmd = ["bash", script_path, configuration_path] + extra_kwargs
        error_found = False
        with Popen(cmd, stderr=PIPE, stdout=PIPE, bufsize=1) as p:
            try:
                db.update_status(exp_id, 'running')
                for line in p.stdout:
                    print_out = line.decode('utf-8')
                    db.update_std(exp_id, print_out, std_type='stdout')
                    print(print_out)
            except KeyboardInterrupt:
                db.update_status(exp_id, 'interrupted')
                print("Experiment Interrupted")
                error_found = True
            finally:
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
                if not error_found:
                    db.update_status(exp_id, 'completed')
                    print("Experiment Done")


def get(_id: int) -> dict:
    """Return the experiment from an id

    Args:
        _id (int): the id of the experiment

    Returns:
        dict:  the experiment document retrieved from the database

    """
    with setup_database() as db:
        experiment = db.get(_id)
    return experiment


def list(*, ids: list, tags: list, query_type: str) -> list:
    """return a list of experiment documents either based on ids or based on tags

    Args:
        ids (list):  a list of ids to retrieve from the database
        tags (list): al list of tags to retrieve from the database
        query_type (str): Can be either 'and' or 'or'. If it is and returns matches that match all tags if it is
            or returns matches that match any tags

    Returns:
            list: A list of dicts with each dict being an experiment document
    """
    with setup_database() as db:
        ids = None if len(ids) == 0 else ids
        tags = None if len(tags) == 0 else tags
        results = db.list_experiments(ids=ids, tags=tags, query_type=query_type)
    return results


def update():
    # TODO be able to update the tags of an experiment or add metadata to it
    pass


def list_tags() -> set:
    """Return all tags in the db
    Returns:
            set: A set of all tags found in the db
    """

    with setup_database() as db:
        results = db.list_experiments()
    return set({tag for exp in results for tag in exp['tags']})


def delete(_id: int) -> None:
    """Delete the document with this id from the database

    Args:
        _id (int): the document id

    """
    with setup_database() as db:
        db.delete(_id)


def count() -> int:
    """Returns the count of all items in the database

    Returns:
        int: The number of items in the database

    """
    with setup_database() as db:
        count = db.count()
    return count


def delete_all() -> None:
    """deletes all items from the database """
    with setup_database() as db:
        db.delete_all()


def get_best():
    # TODO write get best exp document, based on some val_ and metrics
    pass


def resume():
    # TODO think on how to resume an experiment without messing up the database
    pass


def export_config():
    # TODO export the config dir/file based on an experiment
    pass
