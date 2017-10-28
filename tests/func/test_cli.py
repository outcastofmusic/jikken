import click
import jikken.cli
from click.testing import CliRunner


def run_experiment_stub(*args, **kwargs):
    click.echo("starting experiment")
    click.echo("experiment finished")


def test_jikken_cli(file_setup, mocker):
    conf_file, script_file, _ = file_setup
    mocker.patch.object(jikken.cli.api, 'run', new=run_experiment_stub)
    runner = CliRunner()
    result = runner.invoke(jikken.cli.jikken_cli, ['run', script_file, "-c", conf_file])
    assert result.exit_code == 0
    assert result.output == "starting experiment\nexperiment finished\n"
