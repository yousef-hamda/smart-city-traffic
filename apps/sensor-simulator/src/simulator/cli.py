"""Command-line interface for the sensor simulator.

Phase 1 skeleton: argument surface and logging are real, the traffic model
(rush-hour curves, hotspots, incident injection, MQTT/HTTP publishing) lands
in Phase 2.
"""

from pathlib import Path

import click
import structlog

from simulator.logging import configure_logging

logger = structlog.get_logger()


@click.group()
def cli() -> None:
    """Jerusalem traffic sensor simulator."""
    configure_logging()


@cli.command()
@click.option("--rate", type=click.IntRange(min=1), default=50, show_default=True,
              help="Events per second across all sensors.")
@click.option("--hotspots", type=click.Path(exists=False, path_type=Path), default=None,
              help="YAML file describing hotspot zones (e.g. config/jerusalem.yaml).")
def run(rate: int, hotspots: Path | None) -> None:
    """Generate live sensor events and publish over MQTT + HTTP."""
    logger.info("simulator_skeleton", mode="run", rate=rate,
                hotspots=str(hotspots) if hotspots else None,
                note="traffic model lands in Phase 2")


@cli.command()
@click.option("--file", "csv_file", type=click.Path(exists=False, path_type=Path),
              required=True, help="CSV scenario to replay (e.g. rush_hour_accident.csv).")
def replay(csv_file: Path) -> None:
    """Replay a recorded scenario CSV at original cadence."""
    logger.info("simulator_skeleton", mode="replay", file=str(csv_file),
                note="replay engine lands in Phase 2")
