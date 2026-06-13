import random

from rl_optimizer.baselines import (
    FixedTimeController,
    MaxPressureController,
    WebsterController,
)
from rl_optimizer.env import TrafficSignalEnv
from rl_optimizer.evaluate import controller_act_fn, evaluate_baselines, run_episode
from rl_optimizer.intersection import build_default_cluster


def test_max_pressure_serves_the_busiest_phase() -> None:
    cluster = build_default_cluster(random.Random(0), n_intersections=1)
    inter = cluster.intersections[0]
    # EW (phase 1 = approaches 1,3) heavily loaded; NS light.
    inter.approaches[0].queue = 1.0
    inter.approaches[2].queue = 1.0
    inter.approaches[1].queue = 30.0
    inter.approaches[3].queue = 25.0
    action = MaxPressureController().act(cluster)
    assert int(action[0]) == 1


def test_webster_plan_has_positive_greens() -> None:
    cluster = build_default_cluster(random.Random(0), n_intersections=2)
    ctrl = WebsterController()
    ctrl._build_plan(cluster)  # noqa: SLF001
    assert all(g > 0 for greens in ctrl._plans for g in greens)  # noqa: SLF001


def test_fixed_time_cycles_phases() -> None:
    cluster = build_default_cluster(random.Random(0), n_intersections=1)
    ctrl = FixedTimeController(green_steps=2)
    seen = {int(ctrl.act(cluster)[0]) for _ in range(8)}
    assert seen == {0, 1}


def test_adaptive_baselines_beat_fixed_time() -> None:
    """Max-pressure should incur less total delay than a blind fixed timer."""
    results = {r.label: r for r in evaluate_baselines(seeds=(0, 1), episode_seconds=1200)}
    assert results["max-pressure"].total_wait < results["fixed-time"].total_wait


def test_run_episode_reports_metrics() -> None:
    env = TrafficSignalEnv(episode_seconds=600, seed=0)
    res = run_episode(env, controller_act_fn(MaxPressureController()), "mp", seed=0)
    assert res.throughput > 0
    assert res.mean_wait_per_vehicle >= 0
    assert isinstance(res.avg_queue, float)
