#!/usr/bin/env python3
"""Seed Postgres with the Jerusalem demo network.

Inserts neighborhoods, road segments, sensors, and cameras derived from
``data/jerusalem_roads.json`` via the simulator's ``network`` module — the
single derivation source, so seeded IDs match generated telemetry exactly.

Schema is owned by the sensor-ingestion service's Flyway migrations; run the
stack once (``make dev`` or ``make dev-infra`` + the ingestion service) before
seeding. Inserts are idempotent upserts — safe to re-run.

Usage:
    pip install -r scripts/seed/requirements.txt
    python3 scripts/seed/seed_postgres.py [--dsn postgresql://...]
"""

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "apps" / "sensor-simulator" / "src"))

from simulator.network import load_network  # noqa: E402

DEFAULT_DSN = "postgresql://traffic:traffic_dev_password@localhost:5432/traffic"

# Rough rectangle half-size for neighborhood polygons, in degrees (~900 m).
NEIGHBORHOOD_HALF_DEG = 0.008


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", default=os.environ.get("POSTGRES_DSN", DEFAULT_DSN))
    args = parser.parse_args()

    try:
        import psycopg
    except ImportError:
        print("psycopg missing — run: pip install -r scripts/seed/requirements.txt")
        return 1

    network = load_network()

    with psycopg.connect(args.dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.road_segments')")
        row = cur.fetchone()
        if row is None or row[0] is None:
            print(
                "Schema not found. Start the stack first so the ingestion "
                "service's Flyway migrations create the tables (make dev)."
            )
            return 1

        for n in network.neighborhoods:
            lat, lon = n.center
            d = NEIGHBORHOOD_HALF_DEG
            cur.execute(
                """
                INSERT INTO neighborhoods (id, name_en, name_he, name_ar, polygon)
                VALUES (%s, %s, %s, %s,
                        ST_MakeEnvelope(%s, %s, %s, %s, 4326))
                ON CONFLICT (id) DO UPDATE SET
                    name_en = EXCLUDED.name_en,
                    name_he = EXCLUDED.name_he,
                    name_ar = EXCLUDED.name_ar,
                    polygon = EXCLUDED.polygon
                """,
                (n.id, n.name_en, n.name_he, n.name_ar, lon - d, lat - d, lon + d, lat + d),
            )

        for s in network.segments:
            cur.execute(
                """
                INSERT INTO road_segments
                    (id, road_id, seq, name_en, name_he, name_ar,
                     neighborhood_id, speed_limit_kmh, geometry)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                        ST_SetSRID(ST_MakeLine(
                            ST_MakePoint(%s, %s), ST_MakePoint(%s, %s)), 4326))
                ON CONFLICT (id) DO UPDATE SET
                    name_en = EXCLUDED.name_en,
                    name_he = EXCLUDED.name_he,
                    name_ar = EXCLUDED.name_ar,
                    neighborhood_id = EXCLUDED.neighborhood_id,
                    speed_limit_kmh = EXCLUDED.speed_limit_kmh,
                    geometry = EXCLUDED.geometry
                """,
                (
                    s.id, s.road_id, s.seq, s.name_en, s.name_he, s.name_ar,
                    s.neighborhood_id, s.speed_limit_kmh,
                    s.start[1], s.start[0], s.end[1], s.end[0],
                ),
            )

        for sensor in network.sensors:
            cur.execute(
                """
                INSERT INTO sensors (id, segment_id, location)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
                ON CONFLICT (id) DO UPDATE SET
                    segment_id = EXCLUDED.segment_id,
                    location = EXCLUDED.location
                """,
                (sensor.id, sensor.segment_id, sensor.lon, sensor.lat),
            )

        for camera in network.cameras:
            cur.execute(
                """
                INSERT INTO cameras (id, segment_id, location, rtsp_url)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
                ON CONFLICT (id) DO UPDATE SET
                    segment_id = EXCLUDED.segment_id,
                    location = EXCLUDED.location,
                    rtsp_url = EXCLUDED.rtsp_url
                """,
                (
                    camera.id, camera.segment_id, camera.lon, camera.lat,
                    f"rtsp://camera-simulator:8554/{camera.id}",
                ),
            )

        conn.commit()

    print(
        f"Seeded {len(network.neighborhoods)} neighborhoods, "
        f"{len(network.segments)} segments, {len(network.sensors)} sensors, "
        f"{len(network.cameras)} cameras."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
