"""Classical signal controllers to benchmark the RL agents against.

These are the standard yardsticks in traffic engineering. An RL policy is only
interesting if it beats them.

- **Fixed-time** — cycles phases on a fixed schedule, ignoring demand. The
  trivial baseline every deployed light improves on.
- **Webster** — sets a cycle length and splits green in proportion to each
  phase's demand (flow / saturation). Webster's optimal cycle length
  ``C = (1.5L + 5) / (1 - Y)`` where ``L`` is total lost time and ``Y`` the sum
  of critical flow ratios. A strong, demand-aware fixed plan.
- **Max-pressure** — a provably stable *adaptive* policy: each step pick the
  phase that maximizes "pressure" (upstream queue minus downstream queue; here,
  the queue served by the phase). No tuning, reacts to live queues.

Each controller exposes ``act(env) -> np.ndarray`` returning a phase per
intersection, so they plug into the same evaluation loop as an RL policy.
"""

from dataclasses import dataclass, field

import numpy as np

from rl_optimizer.intersection import SATURATION_FLOW_VPS, IntersectionCluster


class Controller:
    name: str = "controller"

    def act(self, cluster: IntersectionCluster) -> np.ndarray:  # pragma: no cover
        raise NotImplementedError


@dataclass
class FixedTimeController(Controller):
    """Round-robin phases on a fixed green duration (in decision steps)."""

    green_steps: int = 6
    name: str = "fixed-time"
    _counters: list[int] = field(default_factory=list)

    def act(self, cluster: IntersectionCluster) -> np.ndarray:
        if not self._counters:
            self._counters = [0] * len(cluster.intersections)
        action = []
        for i, inter in enumerate(cluster.intersections):
            self._counters[i] += 1
            if self._counters[i] >= self.green_steps:
                self._counters[i] = 0
                action.append((inter.current_phase + 1) % len(inter.phases))
            else:
                action.append(inter.current_phase)
        return np.asarray(action, dtype=np.int64)


@dataclass
class WebsterController(Controller):
    """Demand-proportional fixed plan using Webster's method.

    Computes each intersection's green split from the smoothed approach demands,
    then serves phases for their computed green time. Recomputes the plan
    periodically so it adapts slowly to the rush-hour curve.
    """

    recompute_every: int = 20
    min_green_steps: int = 2
    name: str = "webster"
    _plans: list[list[int]] = field(default_factory=list)
    _phase_idx: list[int] = field(default_factory=list)
    _step_in_phase: list[int] = field(default_factory=list)
    _ticks: int = 0

    # Decision step length (s) and Webster cycle bounds (s).
    decision_interval_s: int = 5
    min_cycle_s: float = 20.0
    max_cycle_s: float = 120.0

    def _build_plan(self, cluster: IntersectionCluster) -> None:
        self._plans = []
        for inter in cluster.intersections:
            # Critical flow ratio per phase = the busiest approach it serves,
            # divided by saturation flow (standard Webster critical-lane method).
            ratios = [
                max(inter.approaches[a].arrival_rate_vps for a in phase) / SATURATION_FLOW_VPS
                for phase in inter.phases
            ]
            y = min(0.9, sum(ratios))  # degree of saturation, capped below 1
            lost = 3.0 * len(inter.phases)
            cycle = (1.5 * lost + 5.0) / (1.0 - y)  # Webster's optimal cycle
            cycle = max(self.min_cycle_s, min(self.max_cycle_s, cycle))
            effective = max(1.0, cycle - lost)
            total_ratio = max(1e-6, sum(ratios))
            greens = [
                max(self.min_green_steps,
                    int(round(effective * (r / total_ratio) / self.decision_interval_s)))
                for r in ratios
            ]
            self._plans.append(greens)

    def act(self, cluster: IntersectionCluster) -> np.ndarray:
        if not self._plans or self._ticks % self.recompute_every == 0:
            self._build_plan(cluster)
            self._phase_idx = [0] * len(cluster.intersections)
            self._step_in_phase = [0] * len(cluster.intersections)
        self._ticks += 1

        action = []
        for i, inter in enumerate(cluster.intersections):
            green = self._plans[i][self._phase_idx[i]]
            self._step_in_phase[i] += 1
            if self._step_in_phase[i] >= green:
                self._step_in_phase[i] = 0
                self._phase_idx[i] = (self._phase_idx[i] + 1) % len(inter.phases)
            action.append(self._phase_idx[i])
        return np.asarray(action, dtype=np.int64)


@dataclass
class MaxPressureController(Controller):
    """Adaptive: serve the phase with the most queued demand each step."""

    name: str = "max-pressure"

    def act(self, cluster: IntersectionCluster) -> np.ndarray:
        action = []
        for inter in cluster.intersections:
            pressures = [
                sum(inter.approaches[a].queue for a in phase) for phase in inter.phases
            ]
            action.append(int(np.argmax(pressures)))
        return np.asarray(action, dtype=np.int64)


BASELINES: dict[str, type[Controller]] = {
    "fixed-time": FixedTimeController,
    "webster": WebsterController,
    "max-pressure": MaxPressureController,
}
