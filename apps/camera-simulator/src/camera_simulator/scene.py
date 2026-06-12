"""Traffic scene model: vehicles moving along lanes, with incident injection.

The scene is a pure simulation step (no rendering, no I/O) so it can be unit
tested deterministically under a fixed RNG seed. ``renderer`` turns a scene
snapshot into pixels; ``publishers`` ship the encoded frames.

Vehicle classes mirror the YOLOv8 labels the vision service detects
(``car``/``bus``/``truck``/``motorcycle``) so the synthetic feed exercises the
same downstream classification path as real footage would.
"""

import random
from dataclasses import dataclass, field
from enum import StrEnum

# Approximate on-screen length (px) and relative spawn weight per class.
VEHICLE_PROFILE: dict[str, tuple[int, float]] = {
    "car": (70, 0.68),
    "motorcycle": (38, 0.12),
    "truck": (120, 0.10),
    "bus": (140, 0.10),
}

VEHICLE_COLORS: dict[str, tuple[int, int, int]] = {
    # BGR (OpenCV order)
    "car": (210, 180, 90),
    "motorcycle": (90, 220, 250),
    "truck": (90, 120, 220),
    "bus": (60, 200, 120),
}


class IncidentKind(StrEnum):
    STOPPED_VEHICLE = "stopped_vehicle"
    WRONG_WAY = "wrong_way"


@dataclass
class Vehicle:
    id: int
    vtype: str
    lane: int
    # Position along the road in [0, 1]; direction sign encodes travel way.
    position: float
    speed: float
    wrong_way: bool = False
    stopped: bool = False

    @property
    def length_px(self) -> int:
        return VEHICLE_PROFILE[self.vtype][0]

    @property
    def color(self) -> tuple[int, int, int]:
        return VEHICLE_COLORS[self.vtype]


@dataclass
class SceneConfig:
    lanes: int = 3
    # Target vehicles on screen per lane at density 1.0.
    vehicles_per_lane: float = 4.0
    # 0 = empty road, 1 = nominal, >1 = congestion.
    density: float = 1.0
    base_speed: float = 0.012  # fraction of road length per frame
    seed: int | None = None


@dataclass
class Scene:
    config: SceneConfig
    rng: random.Random = field(init=False)
    vehicles: list[Vehicle] = field(default_factory=list)
    _next_id: int = 1
    frame_index: int = 0
    active_incidents: dict[int, IncidentKind] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.config.seed)
        self._seed_initial_vehicles()

    @property
    def target_count(self) -> int:
        return max(
            0,
            round(self.config.lanes * self.config.vehicles_per_lane * self.config.density),
        )

    def _pick_type(self) -> str:
        types = list(VEHICLE_PROFILE)
        weights = [VEHICLE_PROFILE[t][1] for t in types]
        return self.rng.choices(types, weights=weights, k=1)[0]

    def _spawn(self, position: float | None = None) -> Vehicle:
        vtype = self._pick_type()
        speed_jitter = self.rng.uniform(0.7, 1.25)
        # Heavier vehicles run a touch slower.
        type_factor = {"car": 1.0, "motorcycle": 1.1, "truck": 0.8, "bus": 0.78}[vtype]
        vehicle = Vehicle(
            id=self._next_id,
            vtype=vtype,
            lane=self.rng.randrange(self.config.lanes),
            position=self.rng.random() if position is None else position,
            speed=self.config.base_speed * speed_jitter * type_factor,
        )
        self._next_id += 1
        return vehicle

    def _seed_initial_vehicles(self) -> None:
        self.vehicles = [self._spawn() for _ in range(self.target_count)]

    def inject_incident(self, kind: IncidentKind) -> int:
        """Force an incident; returns the affected vehicle id (-1 if none)."""
        if not self.vehicles:
            self.vehicles.append(self._spawn(position=0.5))
        vehicle = self.rng.choice(self.vehicles)
        if kind is IncidentKind.STOPPED_VEHICLE:
            vehicle.stopped = True
            vehicle.speed = 0.0
        else:
            vehicle.wrong_way = True
        self.active_incidents[vehicle.id] = kind
        return vehicle.id

    def step(self) -> None:
        """Advance one frame: move vehicles, recycle exits, hold density."""
        self.frame_index += 1
        for vehicle in self.vehicles:
            if vehicle.stopped:
                continue
            direction = -1.0 if vehicle.wrong_way else 1.0
            vehicle.position += direction * vehicle.speed

        # Recycle vehicles that left the frame (unless they are a held incident).
        survivors: list[Vehicle] = []
        for vehicle in self.vehicles:
            if 0.0 <= vehicle.position <= 1.0 or vehicle.id in self.active_incidents:
                survivors.append(vehicle)
        self.vehicles = survivors

        # Maintain target density by spawning fresh vehicles at the inflow edge.
        while len(self.vehicles) < self.target_count:
            self.vehicles.append(self._spawn(position=0.0))

    def snapshot(self) -> list[Vehicle]:
        return list(self.vehicles)
