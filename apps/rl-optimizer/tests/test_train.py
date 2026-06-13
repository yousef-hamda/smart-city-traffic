"""Training smoke tests — marked slow; skipped when SB3/torch aren't installed."""

import pytest

sb3 = pytest.importorskip("stable_baselines3")  # noqa: F841


@pytest.mark.slow
def test_dqn_trains_and_saves(tmp_path) -> None:
    from rl_optimizer.train import train

    artifact = train("dqn", timesteps=400, episode_seconds=120, out=tmp_path, use_mlflow=False)
    assert artifact.exists()
    assert artifact.suffix == ".zip"


@pytest.mark.slow
def test_ppo_trains_and_saves(tmp_path) -> None:
    from rl_optimizer.train import train

    artifact = train("ppo", timesteps=512, episode_seconds=120, out=tmp_path, use_mlflow=False)
    assert artifact.exists()


@pytest.mark.slow
def test_flatten_adapter_round_trips_actions() -> None:
    from rl_optimizer.env import TrafficSignalEnv
    from rl_optimizer.train import FlattenMultiDiscrete

    wrapped = FlattenMultiDiscrete(TrafficSignalEnv(n_intersections=3, seed=0))
    # Every discrete action decodes to a valid per-intersection phase vector.
    for a in range(wrapped.n):
        decoded = wrapped._decode(a)  # noqa: SLF001
        assert decoded.shape == (3,)
        assert all(0 <= int(p) <= 1 for p in decoded)
