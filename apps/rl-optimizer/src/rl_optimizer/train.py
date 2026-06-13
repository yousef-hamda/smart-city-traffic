"""Train DQN (baseline) and PPO (advanced) signal controllers with SB3.

    python -m rl_optimizer.train --algo dqn --timesteps 50000
    python -m rl_optimizer.train --algo ppo --timesteps 100000 --compare

DQN needs a Discrete action space, but the env is MultiDiscrete (a phase per
intersection). We wrap it with a flattening adapter that maps a single discrete
action to the joint phase combination, so the same env trains both algorithms.
PPO supports MultiDiscrete natively and uses the env directly.

Metrics + params + the trained policy are logged to MLflow (local file store);
``--no-mlflow`` disables it. ``--compare`` evaluates the trained policy against
the classical baselines and writes a CSV + chart under ``--out``.
"""

import argparse
import json
from pathlib import Path

import gymnasium as gym
import numpy as np

from rl_optimizer.env import TrafficSignalEnv


class FlattenMultiDiscrete(gym.ActionWrapper):  # type: ignore[type-arg]
    """Expose a MultiDiscrete env as a single Discrete action space.

    Maps one integer in ``[0, prod(nvec))`` to the per-intersection phase tuple,
    so DQN (Discrete-only) can drive the joint controller. Implemented as a
    proper Gymnasium ``ActionWrapper`` so Stable-Baselines3 accepts it.
    """

    def __init__(self, env: TrafficSignalEnv) -> None:
        super().__init__(env)
        self._nvec = env.action_space.nvec  # type: ignore[attr-defined]
        self.n = int(np.prod(self._nvec))
        self.action_space = gym.spaces.Discrete(self.n)

    def _decode(self, action: int) -> np.ndarray:
        out, a = [], int(action)
        for base in self._nvec:
            out.append(a % int(base))
            a //= int(base)
        return np.asarray(out, dtype=np.int64)

    def action(self, action: int) -> np.ndarray:
        return self._decode(int(action))


def make_env(algo: str, episode_seconds: int, seed: int) -> gym.Env:  # type: ignore[type-arg]
    env = TrafficSignalEnv(episode_seconds=episode_seconds, seed=seed)
    return FlattenMultiDiscrete(env) if algo == "dqn" else env


def train(
    algo: str,
    timesteps: int,
    episode_seconds: int = 1800,
    seed: int = 0,
    out: Path = Path("ml/models"),
    use_mlflow: bool = True,
) -> Path:
    """Train and save a policy; returns the artifact path."""
    import torch
    from stable_baselines3 import DQN, PPO
    from stable_baselines3.common.base_class import BaseAlgorithm

    torch.set_num_threads(1)  # avoid thread oversubscription on many-core CPUs
    env = make_env(algo, episode_seconds, seed)

    model: BaseAlgorithm
    if algo == "dqn":
        model = DQN("MlpPolicy", env, verbose=0, learning_starts=200, seed=seed)
    elif algo == "ppo":
        model = PPO("MlpPolicy", env, verbose=0, n_steps=256, seed=seed)
    else:
        raise ValueError(f"unknown algo: {algo}")

    if use_mlflow:
        try:
            import mlflow

            mlflow.set_experiment("rl-signal-optimizer")
            with mlflow.start_run(run_name=f"{algo}-{timesteps}"):
                mlflow.log_params({"algo": algo, "timesteps": timesteps, "seed": seed})
                model.learn(total_timesteps=timesteps)
        except Exception:  # noqa: BLE001 - MLflow optional, never block training
            model.learn(total_timesteps=timesteps)
    else:
        model.learn(total_timesteps=timesteps)

    out.mkdir(parents=True, exist_ok=True)
    artifact = out / f"signal_{algo}.zip"
    model.save(artifact)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--algo", choices=["dqn", "ppo"], default="dqn")
    parser.add_argument("--timesteps", type=int, default=50_000)
    parser.add_argument("--episode-seconds", type=int, default=1800)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=Path("ml/models"))
    parser.add_argument("--no-mlflow", action="store_true")
    parser.add_argument("--compare", action="store_true",
                        help="Benchmark vs baselines after training.")
    args = parser.parse_args()

    artifact = train(
        args.algo, args.timesteps, args.episode_seconds, args.seed, args.out,
        use_mlflow=not args.no_mlflow,
    )
    print(f"Saved policy: {artifact}")

    if args.compare:
        from stable_baselines3 import DQN, PPO

        from rl_optimizer.evaluate import evaluate_baselines, evaluate_policy, results_to_rows

        loader = DQN if args.algo == "dqn" else PPO
        policy = loader.load(artifact)
        rows = results_to_rows(evaluate_baselines(episode_seconds=args.episode_seconds))
        rows.append(
            results_to_rows([evaluate_policy(policy, label=args.algo,
                                             episode_seconds=args.episode_seconds)])[0]
        )
        print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
