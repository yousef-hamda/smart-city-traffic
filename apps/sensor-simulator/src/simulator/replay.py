"""CSV scenario replay.

Scenario files (see ``ml/data/scenarios/``) hold pre-recorded readings with a
relative ``offset_s`` column so a demo replays identically every time:

    offset_s,sensor_id,lat,lon,vehicle_count,avg_speed_kmh,occupancy_pct
    0,S-jaffa-road-00-1,31.776,35.227,12,38.5,22.0
"""

import csv
import time
from datetime import datetime, timedelta
from pathlib import Path

import structlog

from simulator.model import Reading
from simulator.publishers import Publisher

logger = structlog.get_logger()

REQUIRED_COLUMNS = frozenset(
    {"offset_s", "sensor_id", "lat", "lon", "vehicle_count", "avg_speed_kmh", "occupancy_pct"}
)


def load_scenario(path: Path) -> list[tuple[float, Reading]]:
    """Parse and validate a scenario CSV into (offset, reading) pairs."""
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"scenario {path} is missing columns: {sorted(missing)}")

        base = datetime.now().astimezone()
        rows: list[tuple[float, Reading]] = []
        for line, row in enumerate(reader, start=2):
            try:
                offset = float(row["offset_s"])
                rows.append(
                    (
                        offset,
                        Reading(
                            sensor_id=row["sensor_id"],
                            ts=(base + timedelta(seconds=offset)).isoformat(),
                            lat=float(row["lat"]),
                            lon=float(row["lon"]),
                            vehicle_count=int(row["vehicle_count"]),
                            avg_speed_kmh=float(row["avg_speed_kmh"]),
                            occupancy_pct=float(row["occupancy_pct"]),
                        ),
                    )
                )
            except (KeyError, ValueError) as exc:
                raise ValueError(f"scenario {path} line {line}: {exc}") from exc

    rows.sort(key=lambda pair: pair[0])
    return rows


def replay(path: Path, publisher: Publisher, speedup: float = 1.0) -> int:
    """Publish a scenario at recorded cadence (``speedup`` x); returns row count."""
    rows = load_scenario(path)
    logger.info("replay_started", file=str(path), rows=len(rows), speedup=speedup)

    started = time.monotonic()
    for offset, reading in rows:
        target = offset / speedup
        delay = target - (time.monotonic() - started)
        if delay > 0:
            time.sleep(delay)
        publisher.publish([reading])

    logger.info("replay_finished", rows=len(rows))
    return len(rows)
