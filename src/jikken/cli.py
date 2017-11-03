import click
import jikken.api as api
from jikken import print_experiment


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version='0.1.0')
def jikken_cli():
    """Run the jikken application"""


@jikken_cli.command(help="run an experiment")
@click.argument('script_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--configuration_path', '-c', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=True))
@click.option('--args', '-a', multiple=True)
@click.option('--tags', '-t', multiple=True)
def run(script_path, configuration_path, args, tags):
    api.run(script_path=script_path, configuration_path=configuration_path, args=args, tags=tags)


@jikken_cli.command(help="list experiments")
@click.option('--ids', '-a', multiple=True)
@click.option('--tags', '-t', multiple=True)
@click.option('--query', '-q', type=click.Choice(['and', 'or']), default='and')
@click.option('--stdout/--no-stdout', default=False)
@click.option('--stderr/--no-stderr', default=False)
@click.option('--var/--no-var', default=True)
@click.option('--git/--no-git', default=True)
def list(ids, tags, query, stdout, stderr, var, git):
    results = api.list(ids=ids, tags=tags, query_type=query)
    for res in results:
        print_experiment(res, stdout=stdout, stderr=stderr, variables=var, git=git)


@jikken_cli.command(help="Return number of experiments in database")
@click.option('--tags', '-t', multiple=True)
@click.option('--query', '-q', type=click.Choice(['and', 'or']), default='and')
def count(tags, query):
    if len(tags) == 0:
        count = api.count()
    else:
        count = len(api.list(ids=[], tags=tags, query_type=query))
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
