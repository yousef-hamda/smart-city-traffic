from click.testing import CliRunner

from simulator.cli import cli


def test_cli_help() -> None:
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_run_command_exits_cleanly() -> None:
    result = CliRunner().invoke(cli, ["run"])
    assert result.exit_code == 0
