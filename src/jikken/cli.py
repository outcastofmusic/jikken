import click
import jikken.api as api

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


if __name__ == '__main__':
    jikken_cli()
