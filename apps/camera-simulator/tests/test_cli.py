from pathlib import Path

from click.testing import CliRunner

from camera_simulator.cli import cli


def test_cli_help() -> None:
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_run_file_output(tmp_path: Path) -> None:
    out = tmp_path / "frames"
    result = CliRunner().invoke(
        cli,
        ["run", "--output", "file", "--out-dir", str(out), "--cameras", "2",
         "--max-frames", "4", "--seed", "1"],
    )
    assert result.exit_code == 0, result.output
    assert len(list(out.glob("*.jpg"))) == 4


def test_run_with_incident(tmp_path: Path) -> None:
    out = tmp_path / "frames"
    result = CliRunner().invoke(
        cli,
        ["run", "--output", "file", "--out-dir", str(out), "--cameras", "1",
         "--max-frames", "2", "--seed", "1", "--incident", "wrong_way"],
    )
    assert result.exit_code == 0, result.output


def test_kafka_output_requires_bootstrap(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        cli, ["run", "--output", "kafka", "--max-frames", "1"], env={"KAFKA_BOOTSTRAP_SERVERS": ""}
    )
    assert result.exit_code != 0
    assert "kafka" in result.output.lower()
