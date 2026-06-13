"""Gymnasium environment for traffic-signal control.

Observation, action, and reward are the interview-critical design choices:

- **Observation** — per intersection: each approach's normalized queue length
  plus a one-hot of the current phase and the time spent in it. Concatenated
  across the cluster. This is what a controller "sees".
- **Action** — MultiDiscrete: one phase index per intersection, chosen each
  decision step. The agent therefore controls every light jointly.
- **Reward** — the negative change in total accumulated delay over the step,
  i.e. we reward *reducing* waiting time. A small switching penalty discourages
  flicker (rapid phase changes that waste lost-time). This "pressure-aware,
  delay-minimizing" shaping is dense (signal every step) and aligns the agent
  with the real objective: throughput up, waiting down.

One environment step = ``decision_interval`` simulated seconds (the controller
commits to a phase for a few seconds, as real controllers do), so the agent
acts at a realistic cadence rather than every single second.
"""

import random
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from rl_optimizer.intersection import IntersectionCluster, build_default_cluster

# Queue length used to normalize observations into ~[0, 1].
QUEUE_NORM = 40.0
# Small tie-breaker against flicker. Must stay well below the per-step delay
# signal (~1+ per step) or the agent learns to never switch and gridlocks.
SWITCH_PENALTY = 0.02


class TrafficSignalEnv(gym.Env[np.ndarray, np.ndarray]):
    """Control a cluster of signals to minimize total vehicle delay."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        n_intersections: int = 4,
        decision_interval: int = 5,
        episode_seconds: int = 3600,
        seed: int | None = None,
    ) -> None:
        super().__init__()
        self.n_intersections = n_intersections
        self.decision_interval = decision_interval
        self.episode_seconds = episode_seconds
        self._seed = seed
        self._cluster: IntersectionCluster = build_default_cluster(
            random.Random(seed), n_intersections
        )

        n_phases = len(self._cluster.intersections[0].phases)
        # One phase choice per intersection.
        self.action_space = spaces.MultiDiscrete([n_phases] * n_intersections)

        approaches = len(self._cluster.intersections[0].approaches)
        # Per intersection: approaches queues + phase one-hot + time-in-phase.
        per_inter = approaches + n_phases + 1
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(per_inter * n_intersections,), dtype=np.float32
        )
        self._steps = 0

    # ------------------------------------------------------------------ #
    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray, dict[str, Any]]:
        super().reset(seed=seed)
        rng = random.Random(self._seed if seed is None else seed)
        self._cluster = build_default_cluster(rng, self.n_intersections)
        self._steps = 0
        return self._observe(), {}

    def _observe(self) -> np.ndarray:
        parts: list[float] = []
        for inter in self._cluster.intersections:
            for app in inter.approaches:
                parts.append(min(1.0, app.queue / QUEUE_NORM))
            phase_onehot = [
                1.0 if i == inter.current_phase else 0.0 for i in range(len(inter.phases))
            ]
            parts.extend(phase_onehot)
            parts.append(min(1.0, inter.time_in_phase / 60.0))
        return np.asarray(parts, dtype=np.float32)

    def step(
        self, action: np.ndarray
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        action = np.atleast_1d(action)
        switches = 0
        for inter, phase in zip(self._cluster.intersections, action, strict=True):
            if int(phase) != inter.current_phase:
                switches += 1
            inter.set_phase(int(phase))

        delay_before = self._cluster.total_wait()
        for _ in range(self.decision_interval):
            self._cluster.step(dt=1.0)
        delay_after = self._cluster.total_wait()

        # Reward = reduction in *new* delay this step, scaled, minus flicker cost.
        new_delay = delay_after - delay_before
        reward = -new_delay / QUEUE_NORM - SWITCH_PENALTY * switches

        self._steps += 1
        terminated = False
        truncated = self._cluster.seconds >= self.episode_seconds
        info = {
            "total_queue": self._cluster.total_queue(),
            "departed": self._cluster.total_departed(),
            "mean_wait": self._cluster.total_wait(),
        }
        return self._observe(), float(reward), terminated, truncated, info

    @property
    def cluster(self) -> IntersectionCluster:
        return self._cluster


class SumoTrafficEnv(TrafficSignalEnv):
    """Placeholder for the SUMO/traci backend.

    When SUMO is installed, this would launch ``sumo`` with a Jerusalem-style
    network via ``traci.start([...])``, read detector occupancies as the
    observation, set tls phases as the action, and read SUMO's waiting-time as
    the reward — keeping the exact same observation/action/reward *contract* as
    the pure-Python env so trained policies transfer. Falls back to the
    Python simulator if ``traci`` is unavailable.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        try:
            import traci  # noqa: F401
            self._sumo_available = True
        except ImportError:
            self._sumo_available = False
        super().__init__(*args, **kwargs)
