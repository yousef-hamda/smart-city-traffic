"""Command-line interface for the sensor simulator.

Examples:
    python -m simulator run --hotspots config/jerusalem.yaml --rate 50
    python -m simulator run --mqtt-host localhost --http-url http://localhost:8081
    python -m simulator replay --file ml/data/scenarios/rush_hour_accident.csv
"""

import random
from pathlib import Path

import click
import structlog
import yaml

from simulator.incidents import IncidentManager
from simulator.logging import configure_logging
from simulator.model import Hotspot, TrafficModel
from simulator.network import load_network
from simulator.publishers import (
    CompositePublisher,
    HttpPublisher,
    MqttPublisher,
    Publisher,
    StdoutPublisher,
)
from simulator.replay import replay as run_replay
from simulator.runner import SimulationRunner

logger = structlog.get_logger()


def _load_hotspots(path: Path | None) -> list[Hotspot]:
    if path is None:
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [
        Hotspot(
            name=h["name"],
            lat=float(h["lat"]),
            lon=float(h["lon"]),
            weight=float(h.get("weight", 0.5)),
            radius_m=float(h.get("radius_m", 800)),
        )
        for h in raw.get("hotspots", [])
    ]


def _build_publisher(mqtt_host: str | None, http_url: str | None, stdout: bool) -> Publisher:
    publishers: list[Publisher] = []
    if mqtt_host:
        publishers.append(MqttPublisher(mqtt_host))
    if http_url:
        publishers.append(HttpPublisher(http_url))
    if stdout or not publishers:
        publishers.append(StdoutPublisher())
    return CompositePublisher(publishers)


@click.group()
def cli() -> None:
    """Jerusalem traffic sensor simulator."""
    configure_logging()


@cli.command()
@click.option("--rate", type=click.IntRange(min=1), default=50, show_default=True,
              help="Target readings per second across the whole network.")
@click.option("--hotspots", type=click.Path(exists=True, path_type=Path), default=None,
              help="YAML file with demand hotspots (e.g. config/jerusalem.yaml).")
@click.option("--network", "network_path", type=click.Path(exists=True, path_type=Path),
              default=None, help="Override the canonical roads JSON.")
@click.option("--mqtt-host", envvar="MQTT_BROKER_HOST", default=None,
              help="MQTT broker host; publishes to sensors/{id}/readings when set.")
@click.option("--http-url", envvar="INGESTION_HTTP_URL", default=None,
              help="Ingestion base URL; POSTs bulk batches when set.")
@click.option("--stdout", "to_stdout", is_flag=True,
              help="Also write NDJSON to stdout (default when no other sink).")
@click.option("--duration", type=float, default=None,
              help="Stop after N seconds (default: run until interrupted).")
@click.option("--incidents-per-hour", type=float, default=0.5, show_default=True,
              help="Expected random incidents per simulated hour.")
@click.option("--seed", type=int, default=None, help="RNG seed for reproducible output.")
def run(
    rate: int,
    hotspots: Path | None,
    network_path: Path | None,
    mqtt_host: str | None,
    http_url: str | None,
    to_stdout: bool,
    duration: float | None,
    incidents_per_hour: float,
    seed: int | None,
) -> None:
    """Generate live sensor events and publish over MQTT / HTTP / stdout."""
    network = load_network(network_path)
    rng = random.Random(seed)
    model = TrafficModel(hotspots=_load_hotspots(hotspots), rng=rng)
    incidents = IncidentManager(
        network=network, rng=rng, incidents_per_hour=incidents_per_hour
    )
    # One reading per sensor per tick → tick interval that hits the target rate.
    interval_s = max(0.2, len(network.sensors) / rate)
    publisher = _build_publisher(mqtt_host, http_url, to_stdout)
    try:
        SimulationRunner(
            network=network,
            model=model,
            incidents=incidents,
            publisher=publisher,
            interval_s=interval_s,
        ).run(duration_s=duration)
    finally:
        publisher.close()


@cli.command()
@click.option("--file", "csv_file", required=True,
              type=click.Path(exists=True, path_type=Path),
              help="Scenario CSV (e.g. ml/data/scenarios/rush_hour_accident.csv).")
@click.option("--mqtt-host", envvar="MQTT_BROKER_HOST", default=None)
@click.option("--http-url", envvar="INGESTION_HTTP_URL", default=None)
@click.option("--stdout", "to_stdout", is_flag=True)
@click.option("--speedup", type=float, default=1.0, show_default=True,
              help="Replay N× faster than recorded.")
def replay(
    csv_file: Path,
    mqtt_host: str | None,
    http_url: str | None,
    to_stdout: bool,
    speedup: float,
) -> None:
    """Replay a recorded scenario CSV at its original cadence."""
    publisher = _build_publisher(mqtt_host, http_url, to_stdout)
    try:
        run_replay(csv_file, publisher, speedup=speedup)
    finally:
        publisher.close()
