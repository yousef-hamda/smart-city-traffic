"""Road-network model derived from the canonical roads file.

Both this simulator and ``scripts/seed/seed_postgres.py`` derive segments,
sensors, and cameras from ``scripts/seed/data/jerusalem_roads.json`` through
this module, so IDs and coordinates always agree between the database seed
and the generated telemetry.

Derivation rules (deterministic):
- one segment per consecutive polyline point pair, id ``{road_id}-{seq:02d}``
- three sensors per segment at 25/50/75% along it, id ``S-{segment_id}-{k}``
- cameras on ~60% of segments (global index ``% 5 not in (1, 3)``),
  id ``C-{segment_id}``
"""

import json
import math
from dataclasses import dataclass
from pathlib import Path

DEFAULT_NETWORK_PATH = (
    Path(__file__).resolve().parents[4] / "scripts" / "seed" / "data" / "jerusalem_roads.json"
)

_SENSOR_POSITIONS = (0.25, 0.50, 0.75)
_CAMERA_SKIP_RESIDUES = frozenset({1, 3})


@dataclass(frozen=True)
class Neighborhood:
    id: str
    name_en: str
    name_he: str
    name_ar: str
    center: tuple[float, float]


@dataclass(frozen=True)
class Segment:
    id: str
    road_id: str
    seq: int
    name_en: str
    name_he: str
    name_ar: str
    neighborhood_id: str
    speed_limit_kmh: int
    start: tuple[float, float]
    end: tuple[float, float]

    @property
    def midpoint(self) -> tuple[float, float]:
        return interpolate(self.start, self.end, 0.5)


@dataclass(frozen=True)
class Sensor:
    id: str
    segment_id: str
    lat: float
    lon: float


@dataclass(frozen=True)
class Camera:
    id: str
    segment_id: str
    lat: float
    lon: float


@dataclass(frozen=True)
class Network:
    neighborhoods: tuple[Neighborhood, ...]
    segments: tuple[Segment, ...]
    sensors: tuple[Sensor, ...]
    cameras: tuple[Camera, ...]

    def segment_by_id(self, segment_id: str) -> Segment:
        try:
            return next(s for s in self.segments if s.id == segment_id)
        except StopIteration:
            raise KeyError(segment_id) from None

    def sensors_for_segment(self, segment_id: str) -> tuple[Sensor, ...]:
        return tuple(s for s in self.sensors if s.segment_id == segment_id)


def interpolate(
    a: tuple[float, float], b: tuple[float, float], t: float
) -> tuple[float, float]:
    """Linear interpolation between two (lat, lon) points — fine at city scale."""
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance in meters between two (lat, lon) points."""
    radius_earth_m = 6_371_000.0
    phi1, phi2 = math.radians(a[0]), math.radians(b[0])
    dphi = math.radians(b[0] - a[0])
    dlam = math.radians(b[1] - a[1])
    h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * radius_earth_m * math.asin(math.sqrt(h))


def load_network(path: Path | None = None) -> Network:
    """Load the canonical roads file and derive the full network."""
    raw = json.loads((path or DEFAULT_NETWORK_PATH).read_text(encoding="utf-8"))

    neighborhoods = tuple(
        Neighborhood(
            id=n["id"],
            name_en=n["name_en"],
            name_he=n["name_he"],
            name_ar=n["name_ar"],
            center=(n["center"][0], n["center"][1]),
        )
        for n in raw["neighborhoods"]
    )

    segments: list[Segment] = []
    for road in raw["roads"]:
        points = [(p[0], p[1]) for p in road["points"]]
        for seq, (start, end) in enumerate(zip(points, points[1:], strict=False)):
            segments.append(
                Segment(
                    id=f"{road['id']}-{seq:02d}",
                    road_id=road["id"],
                    seq=seq,
                    name_en=road["name_en"],
                    name_he=road["name_he"],
                    name_ar=road["name_ar"],
                    neighborhood_id=road["neighborhood_id"],
                    speed_limit_kmh=road["speed_limit_kmh"],
                    start=start,
                    end=end,
                )
            )

    sensors = tuple(
        Sensor(
            id=f"S-{segment.id}-{k}",
            segment_id=segment.id,
            lat=interpolate(segment.start, segment.end, t)[0],
            lon=interpolate(segment.start, segment.end, t)[1],
        )
        for segment in segments
        for k, t in enumerate(_SENSOR_POSITIONS, start=1)
    )

    cameras = tuple(
        Camera(
            id=f"C-{segment.id}",
            segment_id=segment.id,
            lat=segment.midpoint[0],
            lon=segment.midpoint[1],
        )
        for idx, segment in enumerate(segments)
        if idx % 5 not in _CAMERA_SKIP_RESIDUES
    )

    return Network(
        neighborhoods=neighborhoods,
        segments=tuple(segments),
        sensors=sensors,
        cameras=cameras,
    )
