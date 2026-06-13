"""Run controllers/agents over the env and compare throughput vs waiting time.

A controller is anything exposing ``act(cluster) -> action`` (the baselines); an
RL policy is anything exposing ``predict(obs) -> (action, _)`` (Stable-Baselines3
models). ``run_episode`` accepts either via a thin adapter, so the comparison
table treats hand-built and learned controllers identically.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from rl_optimizer.baselines import BASELINES, Controller
from rl_optimizer.env import TrafficSignalEnv

ActFn = Callable[[TrafficSignalEnv, np.ndarray], np.ndarray]


@dataclass
class EpisodeResult:
    label: str
    throughput: int  # vehicles discharged
    total_wait: float  # vehicle-seconds of delay
    mean_wait_per_vehicle: float
    avg_queue: float


def controller_act_fn(controller: Controller) -> ActFn:
    return lambda env, _obs: controller.act(env.cluster)


def policy_act_fn(policy: object) -> ActFn:
    def _act(env: TrafficSignalEnv, obs: np.ndarray) -> np.ndarray:
        action, _ = policy.predict(obs, deterministic=True)  # type: ignore[attr-defined]
        return np.asarray(action)

    return _act


def run_episode(env: TrafficSignalEnv, act: ActFn, label: str, seed: int = 0) -> EpisodeResult:
    # env may be wrapped (e.g. FlattenMultiDiscrete); reach the base for metrics.
    base: TrafficSignalEnv = env.unwrapped  # type: ignore[assignment]
    obs, _ = env.reset(seed=seed)
    queues: list[float] = []
    done = False
    while not done:
        action = act(base, obs)
        obs, _reward, terminated, truncated, info = env.step(action)
        queues.append(float(info["total_queue"]))
        done = terminated or truncated

    throughput = base.cluster.total_departed()
    total_wait = base.cluster.total_wait()
    return EpisodeResult(
        label=label,
        throughput=throughput,
        total_wait=round(total_wait, 1),
        mean_wait_per_vehicle=round(total_wait / max(1, throughput), 2),
        avg_queue=round(float(np.mean(queues)) if queues else 0.0, 2),
    )


def evaluate_baselines(
    seeds: tuple[int, ...] = (0, 1, 2), episode_seconds: int = 1800
) -> list[EpisodeResult]:
    """Average each classical baseline over several seeds."""
    results: list[EpisodeResult] = []
    for name, factory in BASELINES.items():
        per_seed = [
            run_episode(
                TrafficSignalEnv(episode_seconds=episode_seconds, seed=s),
                controller_act_fn(factory()),
                name,
                seed=s,
            )
            for s in seeds
        ]
        results.append(_average(name, per_seed))
    return results


def _eval_env(policy: object, episode_seconds: int, seed: int) -> TrafficSignalEnv:
    """Build an env matching the policy's action space.

    A DQN policy was trained on the flattened Discrete action space, so its
    env must be wrapped to decode the scalar action back to per-intersection
    phases; a PPO policy uses the native MultiDiscrete env directly.
    """
    import gymnasium as gym

    env = TrafficSignalEnv(episode_seconds=episode_seconds, seed=seed)
    space = getattr(policy, "action_space", None)
    if isinstance(space, gym.spaces.Discrete):
        from rl_optimizer.train import FlattenMultiDiscrete

        return FlattenMultiDiscrete(env)  # type: ignore[return-value]
    return env


def evaluate_policy(
    policy: object,
    label: str = "rl",
    seeds: tuple[int, ...] = (0, 1, 2),
    episode_seconds: int = 1800,
) -> EpisodeResult:
    per_seed = [
        run_episode(
            _eval_env(policy, episode_seconds, s),
            policy_act_fn(policy),
            label,
            seed=s,
        )
        for s in seeds
    ]
    return _average(label, per_seed)


def _average(label: str, runs: list[EpisodeResult]) -> EpisodeResult:
    n = len(runs)
    return EpisodeResult(
        label=label,
        throughput=round(sum(r.throughput for r in runs) / n),
        total_wait=round(sum(r.total_wait for r in runs) / n, 1),
        mean_wait_per_vehicle=round(sum(r.mean_wait_per_vehicle for r in runs) / n, 2),
        avg_queue=round(sum(r.avg_queue for r in runs) / n, 2),
    )


def results_to_rows(results: list[EpisodeResult]) -> list[dict[str, object]]:
    return [
        {
            "controller": r.label,
            "throughput": r.throughput,
            "total_wait_s": r.total_wait,
            "mean_wait_per_vehicle_s": r.mean_wait_per_vehicle,
            "avg_queue": r.avg_queue,
        }
        for r in results
    ]
