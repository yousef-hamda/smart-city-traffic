"""Tests for the road-graph derivation and reference algorithms.

Run from the repo root:
    PYTHONPATH=apps/sensor-simulator/src:scripts/seed \
      python -m pytest scripts/seed/tests -q
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "seed"))
sys.path.insert(0, str(REPO_ROOT / "apps" / "sensor-simulator" / "src"))

from graph_model import (  # noqa: E402
    build_graph,
    reachability_impact,
    reachable_from,
    shortest_path,
)
from simulator.network import load_network  # noqa: E402


def _graph():
    return build_graph(load_network())


def test_graph_has_expected_scale() -> None:
    graph = _graph()
    assert len(graph.segment_ids()) == 49
    assert len(graph.edges) > 60
    # A handful of real cross-road junctions, not one per sequential joint.
    assert 1 <= len(graph.intersections) <= 12


def test_sequential_segments_are_bidirectionally_connected() -> None:
    graph = _graph()
    fwd = {(e.source, e.target) for e in graph.edges}
    assert ("jaffa-road-00", "jaffa-road-01") in fwd
    assert ("jaffa-road-01", "jaffa-road-00") in fwd


def test_edges_have_positive_freeflow_time() -> None:
    graph = _graph()
    assert graph.edges
    assert all(e.freeflow_time_s > 0 and e.length_m > 0 for e in graph.edges)


def test_shortest_path_along_a_road() -> None:
    graph = _graph()
    path, cost = shortest_path(graph, "jaffa-road-00", "jaffa-road-04")
    assert path[0] == "jaffa-road-00"
    assert path[-1] == "jaffa-road-04"
    assert cost > 0


def test_live_weights_change_the_route_cost() -> None:
    graph = _graph()
    _, base = shortest_path(graph, "jaffa-road-00", "jaffa-road-04")
    # Make one mid segment extremely slow (an incident): cost must rise.
    slow = {"jaffa-road-02": 10_000.0}
    _, congested = shortest_path(graph, "jaffa-road-00", "jaffa-road-04", weights=slow)
    assert congested > base


def test_unreachable_returns_infinity() -> None:
    graph = _graph()
    path, cost = shortest_path(graph, "jaffa-road-00", "does-not-exist")
    assert path == [] and cost == float("inf")


def test_reachable_from_includes_self_and_neighbors() -> None:
    graph = _graph()
    reach = reachable_from(graph, "jaffa-road-00")
    assert "jaffa-road-00" in reach
    assert "jaffa-road-01" in reach


def test_blocking_a_segment_shrinks_reachability() -> None:
    graph = _graph()
    full = reachable_from(graph, "jaffa-road-00")
    blocked = reachable_from(graph, "jaffa-road-00", blocked={"jaffa-road-02"})
    assert len(blocked) < len(full)


def test_reachability_impact_reports_closed_segment() -> None:
    graph = _graph()
    impact = reachability_impact(graph, "jaffa-road-02")
    assert impact["closed_segment"] == "jaffa-road-02"
    assert "isolated_segments" in impact
