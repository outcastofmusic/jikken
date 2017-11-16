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
    result = runner.invoke(jikken.cli.jikken_cli, ['run', script_file, "-c", conf_file, "-n", "test"])
    assert result.exit_code == 0
    assert result.output == "starting experiment\nexperiment finished\n"


def list_stub(*args, **kwargs):
    return [
            {"name":"test_{}".format(index),"stdout": "hi", "stderr": "bye",
         "variables": {"index": index},
         "id": index, "status": "done",
         "parameter_hash": "123",
         "schema_hash": "456",
         "type": "experiment",
         "commit_id": "cid",
         "dirty": "False",
         "repo": "url",
         "monitored": {},
         "tags": ["hi"]}
        for index in
        range(2)]


def list_tags_stub():
    return {"tag1", "tag2"}


def test_jikken_cli_list_tags(mocker):
    mocker.patch.object(jikken.cli.api, 'list_tags', new=list_tags_stub)
    runner = CliRunner()
    result = runner.invoke(jikken.cli.jikken_cli, ["list","tags"])
    assert result.exit_code == 0
    tags = result.output.split("\n")[1]
    expected_tags = list_tags_stub()
    for tag in expected_tags:
        assert tag in tags


def test_jikken_cli_list(mocker):
    mocker.patch.object(jikken.cli.api, 'list_experiments', new=list_stub)
    runner = CliRunner()
    result = runner.invoke(jikken.cli.jikken_cli, ['list', "exp", "--stdout", "--stderr", "--no-monitored", "--no-git"])
    expected_results = \
            """ name :  test_0  |  id :  0  |  status :  done  |  tags :  ['hi']  \n schema hash :  456  |  param hash :  123  \n\n\n                                              variables                                             \n{'index': 0}\n\n\n                                               stdout                                               \n'hi'\n\n\n                                               stderr                                               \n'bye'\n----------------------------------------------------------------------------------------------------\n name :  test_1  |  id :  1  |  status :  done  |  tags :  ['hi']  \n schema hash :  456  |  param hash :  123  \n\n\n                                              variables                                             \n{'index': 1}\n\n\n                                               stdout                                               \n'hi'\n\n\n                                               stderr                                               \n'bye'\n----------------------------------------------------------------------------------------------------\n"""
    assert result.output.replace(" ", "") == expected_results.replace(" ", "")
    assert result.exit_code == 0


def test_jikken_cli_list_no_args(mocker):
    mocker.patch.object(jikken.cli.api, 'list_experiments', new=list_stub)
    runner = CliRunner()
    result = runner.invoke(jikken.cli.jikken_cli, ['list', "exp"])
    expected_results = \
            """ name :  test_0  |  id :  0  |  status :  done  |  tags :  ['hi']  \n schema hash :  456  |  param hash :  123  \n commit :  cid   |  dirty :  False   |  repo :  url  \n\n\n                                              variables                                             \n{'index': 0}\n----------------------------------------------------------------------------------------------------\n name :  test_1  |  id :  1  |  status :  done  |  tags :  ['hi']  \n schema hash :  456  |  param hash :  123  \n commit :  cid   |  dirty :  False   |  repo :  url  \n\n\n                                              variables                                             \n{'index': 1}\n----------------------------------------------------------------------------------------------------\n"""
    assert result.output.replace(" ", "") == expected_results.replace(" ", "")
    assert result.exit_code == 0
