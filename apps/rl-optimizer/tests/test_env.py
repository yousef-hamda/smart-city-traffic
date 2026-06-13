import numpy as np

from rl_optimizer.env import TrafficSignalEnv


def test_reset_returns_valid_observation() -> None:
    env = TrafficSignalEnv(n_intersections=4, seed=0)
    obs, info = env.reset(seed=0)
    assert env.observation_space.contains(obs)
    assert isinstance(info, dict)


def test_step_contract() -> None:
    env = TrafficSignalEnv(n_intersections=4, seed=0)
    env.reset(seed=0)
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    assert env.observation_space.contains(obs)
    assert isinstance(reward, float)
    assert isinstance(terminated, bool) and isinstance(truncated, bool)
    assert {"total_queue", "departed", "mean_wait"} <= set(info)


def test_episode_terminates_by_time() -> None:
    env = TrafficSignalEnv(n_intersections=2, episode_seconds=60, decision_interval=5, seed=0)
    env.reset(seed=0)
    steps, done = 0, False
    while not done and steps < 100:
        _, _, term, trunc, _ = env.step(env.action_space.sample())
        done = term or trunc
        steps += 1
    assert done
    assert steps <= 13  # 60s / 5s per step + slack


def test_reward_penalizes_queues() -> None:
    """A heavily congested step should yield a more negative reward."""
    env = TrafficSignalEnv(n_intersections=1, seed=0)
    env.reset(seed=0)
    # Force a big queue on a red approach, then take a no-op-ish action.
    for app in env.cluster.intersections[0].approaches:
        app.queue = 50.0
    action = np.zeros(env.action_space.shape, dtype=np.int64)
    _, reward, _, _, _ = env.step(action)
    assert reward < 0
