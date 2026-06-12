"""Derive camera→segment mappings that match the database seed.

The seed (``scripts/seed/seed_postgres.py`` via the sensor-simulator's
``network`` module) places a camera on a segment when its global index
``% 5 not in (1, 3)`` and names it ``C-{segment_id}``. We replicate that exact
rule here — rather than importing across app boundaries — so the frames this
simulator publishes carry camera ids that already exist in Postgres.
"""

import json
from pathlib import Path

DEFAULT_NETWORK_PATH = (
    Path(__file__).resolve().parents[4] / "scripts" / "seed" / "data" / "jerusalem_roads.json"
)

_CAMERA_SKIP_RESIDUES = frozenset({1, 3})


def derive_cameras(network_path: Path | None = None) -> list[tuple[str, str]]:
    """Return ``(camera_id, segment_id)`` pairs matching the DB seed."""
    path = network_path or DEFAULT_NETWORK_PATH
    raw = json.loads(path.read_text(encoding="utf-8"))

    segment_ids: list[str] = []
    for road in raw["roads"]:
        points = road["points"]
        for seq in range(len(points) - 1):
            segment_ids.append(f"{road['id']}-{seq:02d}")

    return [
        (f"C-{segment_id}", segment_id)
        for idx, segment_id in enumerate(segment_ids)
        if idx % 5 not in _CAMERA_SKIP_RESIDUES
    ]
