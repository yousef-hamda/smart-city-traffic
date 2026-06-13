import random

from rl_optimizer.intersection import build_default_cluster


def test_cluster_shape() -> None:
    cluster = build_default_cluster(random.Random(0), n_intersections=4)
    assert len(cluster.intersections) == 4
    assert len(cluster.intersections[0].approaches) == 4
    assert len(cluster.intersections[0].phases) == 2


def test_green_approach_discharges_queue() -> None:
    cluster = build_default_cluster(random.Random(0), n_intersections=1)
    inter = cluster.intersections[0]
    inter.approaches[0].queue = 20.0  # N approach
    inter.set_phase(0)  # NS green (serves approaches 0 and 2)
    for _ in range(10):  # past the lost time, then discharge
        cluster.step()
    assert inter.approaches[0].queue < 20.0


def test_red_approach_does_not_discharge() -> None:
    cluster = build_default_cluster(random.Random(0), n_intersections=1)
    inter = cluster.intersections[0]
    inter.approaches[1].queue = 15.0  # E approach
    inter.set_phase(0)  # NS green — E is red
    start = inter.approaches[1].queue
    for _ in range(10):
        cluster.step()
    # E only grows (arrivals) while red; never served.
    assert inter.approaches[1].queue >= start


def test_switching_incurs_lost_time() -> None:
    cluster = build_default_cluster(random.Random(0), n_intersections=1)
    inter = cluster.intersections[0]
    inter.approaches[0].queue = 30.0
    inter.set_phase(0)
    cluster.step()  # one second of lost time, no discharge yet
    inter.set_phase(1)  # switch away
    assert inter.lost_time_remaining > 0


def test_demand_multiplier_peaks_at_center() -> None:
    cluster = build_default_cluster(random.Random(0))
    cluster.seconds = cluster.peak_center_s
    peak = cluster.demand_multiplier()
    cluster.seconds = 0
    off = cluster.demand_multiplier()
    assert peak > off
