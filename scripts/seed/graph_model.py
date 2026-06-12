"""Derive the road-network knowledge graph from the canonical roads file.

Nodes:  RoadSegment, Intersection, Neighborhood, Sensor (Incident nodes are
        created at runtime, not seeded).
Edges:  (:RoadSegment)-[:CONNECTS_TO]->(:RoadSegment)   travel edges
        (:RoadSegment)-[:IN_NEIGHBORHOOD]->(:Neighborhood)
        (:Sensor)-[:OBSERVED_BY?]  -> actually (:RoadSegment)-[:OBSERVED_BY]->(:Sensor)
        (:RoadSegment)-[:MEETS_AT]->(:Intersection)

Two segments connect when they share an endpoint:
- **sequential** — consecutive segments of the same road always share one;
- **intersection** — endpoints of segments from different roads that fall
  within ``INTERSECTION_RADIUS_M`` of each other are treated as the same
  junction, which becomes an :Intersection node.

Edge weight is free-flow travel time ``length_m / (speed_limit / 3.6)``; the
realtime layer overwrites a ``current_time_s`` property from live speeds so
shortest-path queries reflect current congestion. This module is pure and
deterministic so it can be unit tested without a database; ``seed_neo4j`` turns
the result into MERGE statements and ``shortest_path`` (Dijkstra) is a
reference implementation the AI assistant can call without Neo4j.
"""

import heapq
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "apps" / "sensor-simulator" / "src"))

from simulator.network import (  # noqa: E402
    Network,
    Segment,
    haversine_m,
    load_network,
)

# Endpoints within this distance are the same junction.
INTERSECTION_RADIUS_M = 130.0


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    length_m: float
    freeflow_time_s: float
    intersection_id: str | None


@dataclass
class RoadGraph:
    network: Network
    edges: list[GraphEdge] = field(default_factory=list)
    intersections: dict[str, list[str]] = field(default_factory=dict)

    def neighbors(self, segment_id: str) -> list[GraphEdge]:
        return [e for e in self.edges if e.source == segment_id]

    def segment_ids(self) -> list[str]:
        return [s.id for s in self.network.segments]


def _segment_length_m(segment: Segment) -> float:
    return haversine_m(segment.start, segment.end)


def _freeflow_time_s(length_m: float, speed_limit_kmh: int) -> float:
    return length_m / max(1.0, speed_limit_kmh / 3.6)


def _cluster_endpoints(
    segments: list[Segment], radius_m: float
) -> dict[str, list[tuple[str, str]]]:
    """Group segment endpoints into junction clusters.

    Returns ``intersection_id -> [(segment_id, "start"|"end"), ...]`` for true
    junctions only — clusters where segments from **two or more distinct
    roads** meet. Same-road sequential joints are handled separately and are
    not intersections.
    """
    road_of = {segment.id: segment.road_id for segment in segments}
    points: list[tuple[str, str, tuple[float, float]]] = []
    for segment in segments:
        points.append((segment.id, "start", segment.start))
        points.append((segment.id, "end", segment.end))

    clusters: list[list[tuple[str, str, tuple[float, float]]]] = []
    for point in points:
        for cluster in clusters:
            if haversine_m(point[2], cluster[0][2]) <= radius_m:
                cluster.append(point)
                break
        else:
            clusters.append([point])

    result: dict[str, list[tuple[str, str]]] = {}
    for idx, cluster in enumerate(clusters):
        members = {(seg_id, end) for seg_id, end, _ in cluster}
        distinct_roads = {road_of[seg_id] for seg_id, _ in members}
        if len(distinct_roads) >= 2:
            result[f"intersection-{idx:03d}"] = sorted(members)
    return result


def build_graph(network: Network, radius_m: float = INTERSECTION_RADIUS_M) -> RoadGraph:
    segments = list(network.segments)
    by_id = {s.id: s for s in segments}
    edges: list[GraphEdge] = []
    seen: set[tuple[str, str]] = set()

    def add_edge(a: str, b: str, intersection_id: str | None) -> None:
        if (a, b) in seen:
            return
        length = _segment_length_m(by_id[b])
        edges.append(
            GraphEdge(
                source=a,
                target=b,
                length_m=round(length, 1),
                freeflow_time_s=round(_freeflow_time_s(length, by_id[b].speed_limit_kmh), 1),
                intersection_id=intersection_id,
            )
        )
        seen.add((a, b))

    # Sequential connectivity along each road (both directions).
    for segment in segments:
        nxt = f"{segment.road_id}-{segment.seq + 1:02d}"
        if nxt in by_id:
            add_edge(segment.id, nxt, None)
            add_edge(nxt, segment.id, None)

    # Cross-road connectivity at clustered intersections.
    clusters = _cluster_endpoints(segments, radius_m)
    intersections: dict[str, list[str]] = {}
    for intersection_id, members in clusters.items():
        member_segments = sorted({seg_id for seg_id, _ in members})
        intersections[intersection_id] = member_segments
        for a in member_segments:
            for b in member_segments:
                if a != b:
                    add_edge(a, b, intersection_id)

    return RoadGraph(network=network, edges=edges, intersections=intersections)


def shortest_path(
    graph: RoadGraph,
    source: str,
    target: str,
    weights: dict[str, float] | None = None,
) -> tuple[list[str], float]:
    """Dijkstra over CONNECTS_TO edges.

    ``weights`` optionally overrides per-segment travel time (segment_id ->
    seconds), modelling live congestion; defaults to free-flow time. Returns
    ``([], inf)`` when the target is unreachable.
    """
    dist: dict[str, float] = {source: 0.0}
    prev: dict[str, str] = {}
    pq: list[tuple[float, str]] = [(0.0, source)]
    visited: set[str] = set()

    while pq:
        cost, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        if node == target:
            break
        for edge in graph.neighbors(node):
            weight = (
                weights.get(edge.target, edge.freeflow_time_s)
                if weights
                else edge.freeflow_time_s
            )
            new_cost = cost + weight
            if new_cost < dist.get(edge.target, float("inf")):
                dist[edge.target] = new_cost
                prev[edge.target] = node
                heapq.heappush(pq, (new_cost, edge.target))

    if target not in dist:
        return [], float("inf")

    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    path.reverse()
    return path, dist[target]


def reachable_from(graph: RoadGraph, source: str, blocked: set[str] | None = None) -> set[str]:
    """Segments reachable from ``source`` with ``blocked`` segments removed."""
    blocked = blocked or set()
    if source in blocked:
        return set()
    seen = {source}
    stack = [source]
    while stack:
        node = stack.pop()
        for edge in graph.neighbors(node):
            if edge.target not in seen and edge.target not in blocked:
                seen.add(edge.target)
                stack.append(edge.target)
    return seen


def reachability_impact(graph: RoadGraph, closed_segment: str) -> dict[str, object]:
    """How closing ``closed_segment`` shrinks reachability network-wide."""
    all_ids = set(graph.segment_ids())
    sources = [s for s in all_ids if s != closed_segment]
    if not sources:
        return {"closed_segment": closed_segment, "lost_pairs": 0, "isolated_segments": []}

    isolated: list[str] = []
    for source in sources:
        before = reachable_from(graph, source)
        after = reachable_from(graph, source, blocked={closed_segment})
        if len(before) - len(after) > 1:  # >1 because the closed node itself drops
            isolated.append(source)
    return {
        "closed_segment": closed_segment,
        "affected_sources": len(isolated),
        "isolated_segments": sorted(isolated),
    }


if __name__ == "__main__":  # pragma: no cover - manual inspection helper
    graph = build_graph(load_network())
    print(f"segments={len(graph.segment_ids())} edges={len(graph.edges)} "
          f"intersections={len(graph.intersections)}")
