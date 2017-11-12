from subprocess import PIPE, Popen

from jikken import MultiStageExperiment
from .multistage import load_stage_metadata

from .database import setup_database, ExperimentQuery
from .setups import ExperimentSetup, MultiStageExperimentSetup
from .experiment import Experiment
from .monitor import capture_value
from .utils import prepare_variables, prepare_command
import os

BUFFER_LIMIT = 1000  # the number of characters added to an std stream before updating the database


def run(*, setup: ExperimentSetup) -> None:
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
    with prepare_variables(config_directory=setup.configuration_path,
                           reference_directory=setup.reference_configuration_path) as vr:
        variables, configuration_path = vr
        extra_vars = {argument[0]: argument[1] for argument in setup.args}
        variables = {**variables, **extra_vars}
        cmd = prepare_command(setup.script_path, configuration_path, setup.args)
        exp = Experiment(name=setup.name,
                         variables=variables,
                         code_dir=os.path.dirname(setup.script_path),
                         tags=setup.tags)
        with setup_database() as db:
            exp_id = db.add(exp)
            run_experiment(db=db, exp_id=exp_id, cmd=cmd)


def run_multistage(*, setup: MultiStageExperimentSetup) -> None:
    with prepare_variables(config_directory=setup.configuration_path,
                           reference_directory=setup.reference_configuration_path) as vr:
        variables, configuration_path = vr
        extra_vars = {argument[0]: argument[1] for argument in setup.args}
        variables = {**variables, **extra_vars}
        cmd = prepare_command(setup.script_path, configuration_path, setup.args)
        exp = Experiment(name=setup.stage_name,
                         variables=variables,
                         code_dir=os.path.dirname(setup.script_path),
                         tags=setup.tags)
        with setup_database() as db:
            if setup.input_path is not None:
                multistage_id = load_stage_metadata(setup.input_path)["id"]
                multi_stage = db.get(multistage_id, collection="msexperiments")
            else:
                multistage = MultiStageExperiment(name=setup.name)
                exp_id = db.add(exp)
                multistage.add(exp, stage_name=setup.stage_name)
                db.add(multistage)
                multistage.export_metadata(setup.output_path)
            run_experiment(db=db, exp_id=exp_id, cmd=cmd)


def run_experiment(*, db, exp_id, cmd):
    error_found = False
    with Popen(cmd, stderr=PIPE, stdout=PIPE, bufsize=1) as p:
        try:
            db.update_status(exp_id, 'running')
            line_buffer = ''
            for line in p.stdout:
                print_out = line.decode('utf-8')
                line_buffer += print_out
                print(print_out)
                if len(line_buffer) > BUFFER_LIMIT:
                    db.update_std(exp_id, line_buffer, std_type='stdout')
                    line_buffer = ''
        except KeyboardInterrupt:
            db.update_status(exp_id, 'interrupted')
            print("Experiment Interrupted")
            error_found = True
        finally:
            if line_buffer != '':
                db.update_std(exp_id, line_buffer, std_type='stdout')
            line_buffer = ''
            for line in p.stderr:
                print_out = line.decode('utf-8')
                monitored = capture_value(print_out)
                if monitored is not None:
                    db.update_monitored(exp_id, monitored[0], monitored[1])
                else:
                    line_buffer += print_out
                    print(print_out)
                if 'Error' in print_out:
                    error_found = True
                    db.update_status(exp_id, 'error')
                    print("Experiment Failed")

            if line_buffer != '':
                db.update_std(exp_id, line_buffer, std_type='stderr')
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


def list(*, query: ExperimentQuery) -> list:
    """return a list of experiment documents either based on ids or based on tags

    Args:
        query: ExperimentQuery with ids, tags, query_type schema and params_schema
        ids (list):  a list of ids to retrieve from the database
        tags (list): al list of tags to retrieve from the database
        query_type (str): Can be either 'and' or 'or'. If it is and returns matches that match all tags if it is
            or returns matches that match any tags
        schema(str): a list of schema hashes to query the db
        param_schema(str): a list of parameter schema hashes to query the db

    Returns:
            list: A list of dicts with each dict being an experiment document
    """
    with setup_database() as db:
        results = db.list_experiments(query=query)
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
