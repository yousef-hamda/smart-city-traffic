"""Incident lifecycle: random injection plus scheduled scenarios.

An active incident shrinks the effective capacity of every sensor on its
segment, which the traffic model turns into higher occupancy and lower speed.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from random import Random

from simulator.network import Network

# Capacity retained while an incident is active on a segment.
INCIDENT_CAPACITY_FACTOR = 0.35


@dataclass(frozen=True)
class Incident:
    segment_id: str
    started_at: datetime
    ends_at: datetime

    def active_at(self, at: datetime) -> bool:
        return self.started_at <= at < self.ends_at


@dataclass
class IncidentManager:
    network: Network
    rng: Random
    # Expected random incidents per simulated hour across the whole network.
    incidents_per_hour: float = 0.5
    min_duration_min: float = 10.0
    max_duration_min: float = 45.0

    def __post_init__(self) -> None:
        self._incidents: list[Incident] = []

    @property
    def incidents(self) -> tuple[Incident, ...]:
        return tuple(self._incidents)

    def inject(self, segment_id: str, at: datetime, duration_min: float) -> Incident:
        """Manually start an incident (also used by scenario replay)."""
        self.network.segment_by_id(segment_id)  # validate; raises KeyError
        incident = Incident(
            segment_id=segment_id,
            started_at=at,
            ends_at=at + timedelta(minutes=duration_min),
        )
        self._incidents.append(incident)
        return incident

    def maybe_inject_random(self, at: datetime, interval_s: float) -> Incident | None:
        """Poisson-arrival random incident for the elapsed tick."""
        probability = self.incidents_per_hour * interval_s / 3600.0
        if self.rng.random() >= probability:
            return None
        segment = self.rng.choice(self.network.segments)
        duration = self.rng.uniform(self.min_duration_min, self.max_duration_min)
        return self.inject(segment.id, at, duration)

    def capacity_factor(self, segment_id: str, at: datetime) -> float:
        if any(i.segment_id == segment_id and i.active_at(at) for i in self._incidents):
            return INCIDENT_CAPACITY_FACTOR
        return 1.0

    def prune(self, at: datetime) -> None:
        self._incidents = [i for i in self._incidents if i.ends_at > at]
