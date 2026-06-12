from pathlib import Path

from click.testing import CliRunner

from simulator.cli import cli


def test_cli_help() -> None:
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_run_short_burst_to_stdout() -> None:
    result = CliRunner().invoke(
        cli, ["run", "--rate", "500", "--duration", "0.1", "--seed", "1", "--stdout"]
    )
    assert result.exit_code == 0
    assert '"sensor_id"' in result.output


def test_run_with_hotspots_config() -> None:
    config = Path(__file__).resolve().parents[1] / "config" / "jerusalem.yaml"
    result = CliRunner().invoke(
        cli,
        ["run", "--rate", "500", "--duration", "0.1", "--seed", "1",
         "--hotspots", str(config), "--stdout"],
    )
    assert result.exit_code == 0


def test_replay_command(tmp_path: Path) -> None:
    scenario = tmp_path / "scenario.csv"
    scenario.write_text(
        "offset_s,sensor_id,lat,lon,vehicle_count,avg_speed_kmh,occupancy_pct\n"
        "0,S-jaffa-road-00-1,31.776,35.227,12,38.5,22.0\n",
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        cli, ["replay", "--file", str(scenario), "--speedup", "100", "--stdout"]
    )
    assert result.exit_code == 0
    assert "S-jaffa-road-00-1" in result.output
