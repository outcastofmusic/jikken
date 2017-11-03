import click
import jikken.cli
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
    return [
        {"stdout": "hi", "stderr": "bye", "variables": {"index": index}, "id": index, "status": "done", "tags": ["hi"]}
        for index in
        range(2)]


def test_jikken_cli_list(mocker):
    mocker.patch.object(jikken.cli.api, 'list', new=list_stub)
    runner = CliRunner()
    result = runner.invoke(jikken.cli.jikken_cli, ['list', "--stdout", "--stderr", "--no-monitored", "--no-git"])
    expected_results = \
"""----------------------------------------------------------------------------------------------------
id: 0 | status: done | tags ['hi']
                                             variables                                              
                                             ----------                                             
{'index': 0}
                                               stdout                                               
                                             ----------                                             
hi
                                               stderr                                               
                                             ----------                                             
bye
----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
id: 1 | status: done | tags ['hi']
                                             variables                                              
                                             ----------                                             
{'index': 1}
                                               stdout                                               
                                             ----------                                             
hi
                                               stderr                                               
                                             ----------                                             
bye
----------------------------------------------------------------------------------------------------
"""
    assert result.output == expected_results
    assert result.exit_code == 0
