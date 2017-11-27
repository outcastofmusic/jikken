import click
import jikken.api as api
from .setups import ExperimentSetup, MultiStageExperimentSetup
from .data_formater import PrintExperiment


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version='0.1.0')
def jikken_cli():
    """Run the jikken application"""
    pass


@jikken_cli.command(help="run a single stage experiment from a script. e.g. jikken run script.py -c config.yaml")
@click.argument('script_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--configuration_path', '-c', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=True),
              help="A file or a directory with files that hold the variables that define the experiment")
@click.option('--name', '-n', required=True, type=str, help="the experiment name")
@click.option('--ref_path', '-r', required=False, type=click.Path(exists=True, file_okay=True, dir_okay=True),
              default=None,
              help="A file or a directory with files that hold the variables that define the experiment")
@click.option('--args', '-a', multiple=True,
              help="extra arguments that can be passed to the script multiple can be added,"
                   "e.g. -a a=2 -a batch_size=63 -a early_stopping=False")
@click.option('--tags', '-t', multiple=True,
              help="tags that can be used to distinguish the experiment inside the database."
                   " Multiple can be added e.g. -t org_name -t small_data -t model_1")
def run(script_path, configuration_path, ref_path, args, tags, name):
    """Runs an experiment"""
    setup = ExperimentSetup(
        name=name,
        script_path=script_path,
        configuration_path=configuration_path,
        args=args,
        tags=tags,
        reference_configuration_path=ref_path
    )
    api.run(setup=setup)


@jikken_cli.group(
    help="run a stage of a multistage experiment from a script. e.g. jikken stage run script.py -c config.yaml")
def stage():
    """Run the stage  group"""
    pass


@stage.command(help="run a stage experiment ")
@click.argument('script_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--input_dir', '-i', required=False, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output_dir', '-o', required=True, type=click.Path(exists=False, file_okay=False, dir_okay=True))
@click.option('--configuration_path', '-c', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=True),
              help="A file or a directory with files that hold the variables that define the experiment")
@click.option('--name', '-n', required=True, type=str, help="the experiment name")
@click.option('--stage_name', '-s', required=True, type=str, help="the stage name")
@click.option('--ref_path', '-r', required=False, type=click.Path(exists=True, file_okay=True, dir_okay=True),
              default=None,
              help="A file or a directory with files that hold the variables that define the experiment")
@click.option('--args', '-a', multiple=True,
              help="extra arguments that can be passed to the script multiple can be added,"
                   "e.g. -a a=2 -a batch_size=63 -a early_stopping=False")
@click.option('--tags', '-t', multiple=True,
              help="tags that can be used to distinguish the experiment inside the database."
                   " Multiple can be added e.g. -t org_name -t small_data -t model_1")
def run(script_path, input_dir, output_dir, configuration_path, ref_path, args, tags, name, stage_name):
    setup = MultiStageExperimentSetup(script_path=script_path,
                                      input_path=input_dir,
                                      output_path=output_dir,
                                      configuration_path=configuration_path,
                                      reference_configuration_path=ref_path,
                                      args=args,
                                      tags=tags,
                                      name=name,
                                      stage_name=stage_name
                                      )
    api.run_stage(setup=setup)


@stage.command(help="resume a stage experiment ")
@click.argument('script_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--input_dir', '-i', required=False, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output_dir', '-o', required=True, type=click.Path(exists=False, file_okay=False, dir_okay=True))
@click.option('--configuration_path', '-c', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=True),
              help="A file or a directory with files that hold the variables that define the experiment")
@click.option('--ref_path', '-r', required=False, type=click.Path(exists=True, file_okay=True, dir_okay=True),
              default=None,
              help="A file or a directory with files that hold the variables that define the experiment")
@click.option('--args', '-a', multiple=True,
              help="extra arguments that can be passed to the script multiple can be added,"
                   "e.g. -a a=2 -a batch_size=63 -a early_stopping=False")
@click.option('--tags', '-t', multiple=True,
              help="tags that can be used to distinguish the experiment inside the database."
                   " Multiple can be added e.g. -t org_name -t small_data -t model_1")
def resume(script_path, input_dir, output_dir, configuration_path, ref_path, args, tags):
    setup = MultiStageExperimentSetup(script_path=script_path,
                                      input_path=input_dir,
                                      output_path=output_dir,
                                      configuration_path=configuration_path,
                                      reference_configuration_path=ref_path,
                                      args=args,
                                      tags=tags,
                                      name="",
                                      stage_name=""
                                      )
    api.resume_stage(setup=setup)


@jikken_cli.group(context_settings={'help_option_names': ['-h', '--help']},
                  help="Retrieve list of experiments from db matching a query")
def list():
    """Run the list command"""
    pass


@list.command(help="(Experiments): list experiments")
@click.option('--ids', '-i', multiple=True, help="the ids to print")
@click.option('--tags', '-t', multiple=True, help="the tags that need to be matched")
@click.option('--names', '-n', multiple=True, help="experiment names that need to be matched")
@click.option('--schema', '-s', multiple=True, help="hash that matches experiment schema hash")
@click.option('--status', type=click.Choice(["running", "error", "interrupted", "completed"]), multiple=True,
              help="status of the experiment")
@click.option('--param_schema', '-p', multiple=True,
              help="hash that matches the experiment schema with parameters hash")
@click.option('--query', '-q', type=click.Choice(['all', 'any']), default='all',
              help="the type of query ot be used (and|or)")
@click.option('--stdout/--no-stdout', default=False, help="print the stdout of the experiments listed")
@click.option('--stderr/--no-stderr', default=False, help="print the stderr of the experiments listed")
@click.option('--var/--no-var', default=True, help="print the configuration variables of the experiments listed")
@click.option('--git/--no-git', default=True, help="print git information of the experiments listed")
@click.option('--monitored/--no-monitored', default=True, help="print monitored variables of the experiments listed")
def exp(ids, query, tags, names, schema, param_schema, status, stdout, stderr, var, git, monitored):
    assert (len(ids) == 0) or (len(tags) == 0), "cannot provide both tags and ids"
    query = api.ExperimentQuery(
        tags=tags,
        names=names,
        ids=ids,
        schema_hashes=schema,
        schema_param_hashes=param_schema,
        query_type=query,
        status=status
    )
    results = api.list_experiments(query=query)
    pe = PrintExperiment(stdout=stdout, stderr=stderr, variables=var, git=git, monitored=monitored)
    for res in results:
        pe.print_experiment(res)


@list.command(help="(Best Experiment): get best experiment based on monitored metric")
@click.option('--ids', '-i', multiple=True, help="the ids to print")
@click.option('--tags', '-t', multiple=True, help="the tags that need to be matched")
@click.option('--names', '-n', multiple=True, help="experiment names that need to be matched")
@click.option('--schema', '-s', multiple=True, help="hash that matches experiment schema hash")
@click.option('--status', type=click.Choice(["running", "error", "interrupted", "completed"]), multiple=True,
              help="status of the experiment")
@click.option('--param_schema', '-p', multiple=True,
              help="hash that matches the experiment schema with parameters hash")
@click.option('--query', '-q', type=click.Choice(['all', 'any']), default='all',
              help="the type of query ot be used (and|or)")
@click.option('--stdout/--no-stdout', default=False, help="print the stdout of the experiments listed")
@click.option('--stderr/--no-stderr', default=False, help="print the stderr of the experiments listed")
@click.option('--var/--no-var', default=True, help="print the configuration variables of the experiments listed")
@click.option('--git/--no-git', default=True, help="print git information of the experiments listed")
@click.option('--monitored/--no-monitored', default=True, help="print monitored variables of the experiments listed")
@click.option('--metric', '-m', required=True,
              help="the metric to compare. If an multiple values have been stored then last one is used")
@click.option('--optimum', required=True, help="compare by searching for a minimum or a maximum",
              type=click.Choice(["min", "max"]), default="min")
def best(ids, query, tags, names, schema, param_schema, status, stdout, stderr, var, git, monitored, optimum, metric):
    assert (len(ids) == 0) or (len(tags) == 0), "cannot provide both tags and ids"
    query = api.ExperimentQuery(
        tags=tags,
        names=names,
        ids=ids,
        schema_hashes=schema,
        schema_param_hashes=param_schema,
        query_type=query,
        status=status
    )
    best_result = api.get_best(query=query, optimum=optimum, metric=metric)
    if best_result is not None:
        print_experiment(best_result, stdout=stdout, stderr=stderr, variables=var, git=git, monitored=monitored)
    else:
        print("No experiment found")


# TODO write cli test for list mse
@list.command(help="(MultiStageExperiments): list multistage experiments")
@click.option('--ids', '-i', multiple=True, help="the ids to print")
@click.option('--names', '-n', multiple=True, help="multistage experiment names that need to be matched")
@click.option('--steps', '-s', multiple=True, help="name of steps in the multistage experiment")
@click.option('--hashes', '-h', multiple=True, help="hash that matches the multistage experiment")
@click.option('--query', '-q', type=click.Choice(['all', 'any']), default='all',
              help="the type of query ot be used (and|or)")
@click.option('--stdout/--no-stdout', default=False, help="print the stdout of the experiments listed")
@click.option('--stderr/--no-stderr', default=False, help="print the stderr of the experiments listed")
@click.option('--var/--no-var', default=True, help="print the configuration variables of the experiments listed")
@click.option('--git/--no-git', default=True, help="print git information of the experiments listed")
@click.option('--monitored/--no-monitored', default=True, help="print monitored variables of the experiments listed")
def mse(ids, query, names, hashes, steps, stdout, stderr, var, git, monitored):
    query = api.MultiStageExperimentQuery(
        names=names,
        ids=ids,
        hashes=hashes,
        query_type=query,
        steps=steps
    )
    results = api.list_multi_stage_experiments(query=query)

    for res in results:
        print_experiment(res, stdout=stdout, stderr=stderr, variables=var, git=git, monitored=monitored)


@list.command(help="list all tags in db")
def tags():
    tags = api.list_tags()
    print("tags".center(100), tags, sep='\n')


@list.command(help="Return total number of experiments in db or number that match tags query")
@click.option('--tags', '-t', multiple=True, help="tags that describe experiment")
@click.option('--query', '-q', type=click.Choice(['all', 'any']), default='all', help="the type of query")
@click.option('--names', '-n', multiple=True, help="experiment names that need to be matched")
def count(tags, query, names):
    if len(tags) == 0 or len(names) == 0:
        count = api.count()
    else:
        query = api.ExperimentQuery(ids=[], names=names, tags=tags, query_type=query)
        count = len(api.list(query=query))
    print("number of items: {}".format(count))


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@jikken_cli.command(help="Clear database of all experiments")
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to drop the db?')
def delete_all():
    api.delete_all()


if __name__ == '__main__':
    jikken_cli()
