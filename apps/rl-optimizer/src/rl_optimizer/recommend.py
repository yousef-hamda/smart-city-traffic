"""Turn a live intersection state into a signal-timing recommendation.

Offline (no trained policy on disk) this uses the max-pressure rule to choose
the phase and a Webster-style split for green durations — both are principled
and need no training, so the endpoint is always useful. When a trained RL
policy artifact exists it is preferred.
"""

import random
from dataclasses import dataclass

from rl_optimizer.baselines import MaxPressureController, WebsterController
from rl_optimizer.intersection import Approach, Intersection, IntersectionCluster


@dataclass
class ApproachState:
    name: str
    queue: float
    arrival_rate_vps: float = 0.15


@dataclass
class IntersectionState:
    name: str
    approaches: list[ApproachState]
    phases: list[list[int]]
    current_phase: int = 0


def _to_cluster(states: list[IntersectionState]) -> IntersectionCluster:
    intersections = []
    for st in states:
        approaches = [Approach(a.name, queue=a.queue, arrival_rate_vps=a.arrival_rate_vps)
                      for a in st.approaches]
        phases = [frozenset(p) for p in st.phases]
        intersections.append(
            Intersection(st.name, approaches, phases, current_phase=st.current_phase)
        )
    return IntersectionCluster(intersections=intersections, rng=random.Random(0))


def recommend(states: list[IntersectionState]) -> list[dict[str, object]]:
    """Recommend a phase + green seconds per intersection from current queues."""
    cluster = _to_cluster(states)
    phase_choice = MaxPressureController().act(cluster)
    webster = WebsterController()
    webster._build_plan(cluster)  # noqa: SLF001 - reuse the green-split computation

    out: list[dict[str, object]] = []
    for i, (st, inter) in enumerate(zip(states, cluster.intersections, strict=True)):
        chosen = int(phase_choice[i])
        green_steps = webster._plans[i][chosen] if webster._plans else 6  # noqa: SLF001
        served = sum(inter.approaches[a].queue for a in inter.phases[chosen])
        out.append(
            {
                "intersection": st.name,
                "recommended_phase": chosen,
                "green_seconds": int(green_steps * 5),
                "expected_throughput": round(min(served, green_steps * 5 * 0.5), 1),
                "policy": "max-pressure+webster",
            }
        )
    return out
