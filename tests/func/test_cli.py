import click
import jikken.cli
import tabulate
from click.testing import CliRunner


def run_experiment_stub(*args, **kwargs):
    click.echo("starting experiment")
    click.echo("experiment finished")


def test_jikken_cli_run(file_setup, mocker):
    conf_file, script_file, _ = file_setup
    mocker.patch.object(jikken.cli.api, 'run', new=run_experiment_stub)
    runner = CliRunner()
    result = runner.invoke(jikken.cli.jikken_cli, ['run', script_file, "-c", conf_file])
    assert result.exit_code == 0
    assert result.output == "starting experiment\nexperiment finished\n"


def list_stub(*args, **kwargs):
    return [{"stdout": "hi", "stderr": "bye", "value": index, "value2": index + 1} for index in range(2)]


def test_jikken_cli_list(mocker):
    mocker.patch.object(jikken.cli.api, 'list', new=list_stub)
    runner = CliRunner()
    result = runner.invoke(jikken.cli.jikken_cli, ['list', "--stdout", "--stderr"])
    assert result.exit_code == 0
    expected_results = tabulate.tabulate(list_stub(), headers="keys") + "\n"
    assert result.output == expected_results
