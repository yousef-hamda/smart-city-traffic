"""Traffic demand model for the Jerusalem network.

Demand follows the Israeli week: Sunday-Thursday are workdays with AM/PM
peaks, Friday has a single pre-Shabbat late-morning peak and collapses in the
afternoon, Saturday stays quiet until Shabbat ends in the evening. Speed is
derived from occupancy with a concave fundamental-diagram approximation, and
hotspots add gaussian-weighted demand around configured points of interest.
"""

import math
import random
from dataclasses import dataclass, field
from datetime import datetime

from simulator.network import Sensor, haversine_m

FRIDAY = 4
SATURDAY = 5

# Vehicles/hour a sensor's lane group can carry at the segment speed limit.
# ~20 veh/h per km/h of speed limit is a serviceable single-corridor proxy.
CAPACITY_PER_KMH = 20.0

MIN_SPEED_KMH = 4.0


@dataclass(frozen=True)
class Hotspot:
    name: str
    lat: float
    lon: float
    weight: float
    radius_m: float


@dataclass(frozen=True)
class Reading:
    sensor_id: str
    ts: str
    lat: float
    lon: float
    vehicle_count: int
    avg_speed_kmh: float
    occupancy_pct: float

    def as_dict(self) -> dict[str, object]:
        return {
            "sensor_id": self.sensor_id,
            "ts": self.ts,
            "lat": self.lat,
            "lon": self.lon,
            "vehicle_count": self.vehicle_count,
            "avg_speed_kmh": self.avg_speed_kmh,
            "occupancy_pct": self.occupancy_pct,
        }


def _gaussian_bump(hour: float, center: float, width: float, height: float) -> float:
    return height * math.exp(-((hour - center) ** 2) / (2 * width**2))


def demand_factor(at: datetime) -> float:
    """Relative demand in [0, 1] for the local time ``at`` (Israeli week)."""
    hour = at.hour + at.minute / 60.0
    weekday = at.weekday()

    if weekday == FRIDAY:
        # Errand rush before Shabbat, then the city winds down.
        factor = 0.10 + _gaussian_bump(hour, 11.0, 2.2, 0.75)
        if hour >= 15.0:
            factor *= max(0.15, 1.0 - (hour - 15.0) / 3.0)
        return min(factor, 1.0)

    if weekday == SATURDAY:
        # Quiet through Shabbat; traffic returns after dark.
        return min(0.08 + _gaussian_bump(hour, 21.0, 1.8, 0.35), 1.0)

    # Sunday-Thursday: bimodal commute peaks.
    factor = (
        0.07
        + _gaussian_bump(hour, 8.0, 1.3, 0.93)
        + _gaussian_bump(hour, 17.5, 1.7, 0.85)
        + _gaussian_bump(hour, 13.0, 2.5, 0.30)
    )
    return min(factor, 1.0)


@dataclass
class TrafficModel:
    """Generates per-sensor readings; deterministic under a fixed RNG seed."""

    hotspots: list[Hotspot] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)

    def hotspot_multiplier(self, sensor: Sensor) -> float:
        multiplier = 1.0
        for hotspot in self.hotspots:
            distance = haversine_m((sensor.lat, sensor.lon), (hotspot.lat, hotspot.lon))
            multiplier += hotspot.weight * math.exp(
                -(distance**2) / (2 * hotspot.radius_m**2)
            )
        return multiplier

    def reading(
        self,
        sensor: Sensor,
        speed_limit_kmh: int,
        at: datetime,
        interval_s: float,
        capacity_factor: float = 1.0,
    ) -> Reading:
        """One observation for ``sensor`` over an ``interval_s`` window ending at ``at``.

        ``capacity_factor`` < 1 models an active incident on the segment:
        the same demand pushes occupancy up and speed down.
        """
        capacity_vph = speed_limit_kmh * CAPACITY_PER_KMH * capacity_factor
        demand_vph = (
            speed_limit_kmh
            * CAPACITY_PER_KMH
            * demand_factor(at)
            * self.hotspot_multiplier(sensor)
            * self.rng.lognormvariate(0.0, 0.10)
        )

        occupancy = min(0.97, 0.85 * demand_vph / capacity_vph)
        flow_vph = min(demand_vph, capacity_vph)

        expected_vehicles = flow_vph * interval_s / 3600.0
        vehicle_count = self._poisson(expected_vehicles)

        # Concave speed-occupancy curve: free flow holds while the road is
        # lightly loaded, then speed collapses as occupancy saturates.
        speed = speed_limit_kmh * (1.0 - occupancy**1.8)
        speed += self.rng.gauss(0.0, 1.5)
        speed = max(MIN_SPEED_KMH, min(speed, speed_limit_kmh * 1.05))

        return Reading(
            sensor_id=sensor.id,
            ts=at.isoformat(),
            lat=round(sensor.lat, 6),
            lon=round(sensor.lon, 6),
            vehicle_count=vehicle_count,
            avg_speed_kmh=round(speed, 1),
            occupancy_pct=round(occupancy * 100.0, 1),
        )

    def _poisson(self, lam: float) -> int:
        """Knuth sampling — lambda stays small (per-interval counts)."""
        if lam <= 0.0:
            return 0
        threshold = math.exp(-lam)
        k, p = 0, 1.0
        while True:
            p *= self.rng.random()
            if p <= threshold:
                return k
            k += 1
