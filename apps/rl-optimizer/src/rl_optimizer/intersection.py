"""A lightweight traffic-intersection-cluster simulator.

SUMO (via ``traci``) is the production microsimulator the spec targets, but it
needs a native binary that isn't available in every environment. So the
default backend is this pure-Python queue model — deterministic, fast, and
dependency-free — which is enough to train and compare signal controllers and
to unit-test the whole RL stack. ``env.SumoTrafficEnv`` documents the traci
backend for when SUMO is installed.

Model: a cluster of signalised intersections, each with ``approaches`` incoming
lanes. Vehicles arrive per approach as a Poisson process with a time-varying
rate (a rush-hour curve). Each intersection runs one **phase** at a time; a
phase gives green to a set of approaches, which then discharge at a saturation
flow. Vehicles on red approaches wait and accumulate delay. Switching phase
costs a fixed amber/clearance time during which nobody moves.
"""

import math
from dataclasses import dataclass, field
from random import Random

# Saturation discharge: vehicles per second a green approach can release.
SATURATION_FLOW_VPS = 0.5
# Lost time (s) when a light changes phase (amber + all-red clearance).
SWITCH_LOST_TIME_S = 3.0


@dataclass
class Approach:
    """One incoming lane group at an intersection."""

    name: str
    queue: float = 0.0
    arrival_rate_vps: float = 0.1
    # Cumulative vehicle-seconds of delay, reset each measurement window.
    cumulative_wait: float = 0.0
    # Vehicles discharged (fractional; rounded only when reported).
    departed: float = 0.0


@dataclass
class Intersection:
    """A single signalised intersection with N approaches and M phases.

    ``phases`` maps a phase index to the set of approach indices that get green.
    A classic 4-way is two phases: {N,S} and {E,W}.
    """

    name: str
    approaches: list[Approach]
    phases: list[frozenset[int]]
    current_phase: int = 0
    # Seconds remaining of lost time after a just-issued phase change.
    lost_time_remaining: float = 0.0
    time_in_phase: float = 0.0

    def set_phase(self, phase: int) -> None:
        if phase != self.current_phase:
            self.current_phase = phase
            self.lost_time_remaining = SWITCH_LOST_TIME_S
            self.time_in_phase = 0.0
        else:
            self.time_in_phase += 1.0

    def green_approaches(self) -> frozenset[int]:
        return self.phases[self.current_phase]

    @property
    def total_queue(self) -> float:
        return sum(a.queue for a in self.approaches)


@dataclass
class IntersectionCluster:
    """A small grid of intersections evolved one second at a time."""

    intersections: list[Intersection]
    rng: Random = field(default_factory=Random)
    seconds: float = 0.0
    # Peak demand multiplier shape over a (simulated) hour, 0..1.
    peak_center_s: float = 1800.0
    peak_width_s: float = 900.0

    def demand_multiplier(self) -> float:
        """A single gaussian rush-hour bump in [~0.2, 1.0]."""
        x = self.seconds
        bump = math.exp(-((x - self.peak_center_s) ** 2) / (2 * self.peak_width_s**2))
        return 0.2 + 0.8 * bump

    def _arrivals(self, rate_vps: float) -> float:
        """Poisson arrivals for a 1-second step (small lambda)."""
        lam = max(0.0, rate_vps * self.demand_multiplier())
        if lam <= 0:
            return 0.0
        # Knuth sampling.
        threshold = math.exp(-lam)
        k, p = 0, 1.0
        while True:
            p *= self.rng.random()
            if p <= threshold:
                return float(k)
            k += 1

    def step(self, dt: float = 1.0) -> float:
        """Advance the whole cluster ``dt`` seconds; return total delay incurred.

        Delay this step = sum of all queued vehicles * dt (vehicle-seconds).
        """
        step_delay = 0.0
        for inter in self.intersections:
            green = inter.green_approaches()
            discharging = inter.lost_time_remaining <= 0.0
            inter.lost_time_remaining = max(0.0, inter.lost_time_remaining - dt)

            for idx, app in enumerate(inter.approaches):
                app.queue += self._arrivals(app.arrival_rate_vps) * dt
                if discharging and idx in green:
                    served = min(app.queue, SATURATION_FLOW_VPS * dt)
                    app.queue -= served
                    app.departed += served
                # Everyone still queued waits another dt.
                app.cumulative_wait += app.queue * dt
                step_delay += app.queue * dt
        self.seconds += dt
        return step_delay

    def total_queue(self) -> float:
        return sum(i.total_queue for i in self.intersections)

    def total_departed(self) -> int:
        return int(sum(a.departed for i in self.intersections for a in i.approaches))

    def total_wait(self) -> float:
        return sum(a.cumulative_wait for i in self.intersections for a in i.approaches)


def build_default_cluster(rng: Random, n_intersections: int = 4) -> IntersectionCluster:
    """A row of 4-way intersections, each with two phases (NS / EW)."""
    intersections = []
    for n in range(n_intersections):
        approaches = [
            Approach("N", arrival_rate_vps=0.09),
            Approach("E", arrival_rate_vps=0.14),
            Approach("S", arrival_rate_vps=0.09),
            Approach("W", arrival_rate_vps=0.14),
        ]
        phases = [frozenset({0, 2}), frozenset({1, 3})]  # NS green, EW green
        intersections.append(Intersection(f"J{n}", approaches, phases))
    return IntersectionCluster(intersections=intersections, rng=rng)
