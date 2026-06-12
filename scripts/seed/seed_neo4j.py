#!/usr/bin/env python3
"""Seed Neo4j with the road-network knowledge graph.

Derives nodes and edges via ``graph_model`` (the same derivation the reference
algorithms and tests use) and MERGEs them into Neo4j. Idempotent — re-running
updates properties in place.

Usage:
    pip install -r scripts/seed/requirements.txt
    python3 scripts/seed/seed_neo4j.py [--uri bolt://localhost:7687] [--password ...]
"""

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "seed"))
sys.path.insert(0, str(REPO_ROOT / "apps" / "sensor-simulator" / "src"))

from graph_model import build_graph  # noqa: E402
from simulator.network import load_network  # noqa: E402

DEFAULT_URI = "bolt://localhost:7687"

CONSTRAINTS = [
    "CREATE CONSTRAINT segment_id IF NOT EXISTS "
    "FOR (s:RoadSegment) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT neighborhood_id IF NOT EXISTS "
    "FOR (n:Neighborhood) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT sensor_id IF NOT EXISTS "
    "FOR (s:Sensor) REQUIRE s.id IS UNIQUE",
    "CREATE CONSTRAINT intersection_id IF NOT EXISTS "
    "FOR (i:Intersection) REQUIRE i.id IS UNIQUE",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uri", default=os.environ.get("NEO4J_URI", DEFAULT_URI))
    parser.add_argument("--user", default=os.environ.get("NEO4J_USER", "neo4j"))
    parser.add_argument(
        "--password",
        default=os.environ.get("NEO4J_PASSWORD", "traffic_dev_password"),
    )
    args = parser.parse_args()

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("neo4j driver missing — run: pip install -r scripts/seed/requirements.txt")
        return 1

    network = load_network()
    graph = build_graph(network)

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    with driver.session() as session:
        for constraint in CONSTRAINTS:
            session.run(constraint)

        # Neighborhoods.
        session.run(
            """
            UNWIND $rows AS row
            MERGE (n:Neighborhood {id: row.id})
            SET n.name_en = row.name_en, n.name_he = row.name_he,
                n.name_ar = row.name_ar, n.lat = row.lat, n.lon = row.lon
            """,
            rows=[
                {
                    "id": n.id, "name_en": n.name_en, "name_he": n.name_he,
                    "name_ar": n.name_ar, "lat": n.center[0], "lon": n.center[1],
                }
                for n in network.neighborhoods
            ],
        )

        # Segments + IN_NEIGHBORHOOD.
        session.run(
            """
            UNWIND $rows AS row
            MERGE (s:RoadSegment {id: row.id})
            SET s.name_en = row.name_en, s.name_he = row.name_he,
                s.name_ar = row.name_ar, s.speed_limit_kmh = row.speed_limit_kmh,
                s.road_id = row.road_id
            WITH s, row
            MATCH (n:Neighborhood {id: row.neighborhood_id})
            MERGE (s)-[:IN_NEIGHBORHOOD]->(n)
            """,
            rows=[
                {
                    "id": s.id, "name_en": s.name_en, "name_he": s.name_he,
                    "name_ar": s.name_ar, "speed_limit_kmh": s.speed_limit_kmh,
                    "road_id": s.road_id, "neighborhood_id": s.neighborhood_id,
                }
                for s in network.segments
            ],
        )

        # Sensors + OBSERVED_BY.
        session.run(
            """
            UNWIND $rows AS row
            MERGE (sensor:Sensor {id: row.id})
            SET sensor.lat = row.lat, sensor.lon = row.lon
            WITH sensor, row
            MATCH (seg:RoadSegment {id: row.segment_id})
            MERGE (seg)-[:OBSERVED_BY]->(sensor)
            """,
            rows=[
                {"id": s.id, "lat": s.lat, "lon": s.lon, "segment_id": s.segment_id}
                for s in network.sensors
            ],
        )

        # Intersections + MEETS_AT.
        session.run(
            """
            UNWIND $rows AS row
            MERGE (i:Intersection {id: row.id})
            WITH i, row
            UNWIND row.segments AS seg_id
            MATCH (s:RoadSegment {id: seg_id})
            MERGE (s)-[:MEETS_AT]->(i)
            """,
            rows=[
                {"id": iid, "segments": segs}
                for iid, segs in graph.intersections.items()
            ],
        )

        # CONNECTS_TO travel edges (freeflow time seeds current_time_s).
        session.run(
            """
            UNWIND $rows AS row
            MATCH (a:RoadSegment {id: row.source})
            MATCH (b:RoadSegment {id: row.target})
            MERGE (a)-[r:CONNECTS_TO]->(b)
            SET r.length_m = row.length_m,
                r.freeflow_time_s = row.freeflow_time_s,
                r.current_time_s = coalesce(r.current_time_s, row.freeflow_time_s),
                r.intersection_id = row.intersection_id
            """,
            rows=[
                {
                    "source": e.source, "target": e.target, "length_m": e.length_m,
                    "freeflow_time_s": e.freeflow_time_s,
                    "intersection_id": e.intersection_id,
                }
                for e in graph.edges
            ],
        )

    driver.close()
    print(
        f"Seeded graph: {len(network.segments)} segments, {len(graph.edges)} "
        f"edges, {len(graph.intersections)} intersections, "
        f"{len(network.sensors)} sensors."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
