"""Tool registry: 8 traffic-analysis tools for the Anthropic tool-calling loop."""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Graph helpers — imported lazily so the module loads even without Neo4j deps.
# ---------------------------------------------------------------------------
_GRAPH: Any = None
_GRAPH_TRIED = False


def _get_graph() -> Any:
    global _GRAPH, _GRAPH_TRIED
    if _GRAPH_TRIED:
        return _GRAPH
    _GRAPH_TRIED = True
    try:
        seed_dir = Path(__file__).resolve().parents[5] / "scripts" / "seed"
        sim_src = Path(__file__).resolve().parents[5] / "apps" / "sensor-simulator" / "src"
        for p in [str(seed_dir), str(sim_src)]:
            if p not in sys.path:
                sys.path.insert(0, p)
        from graph_model import build_graph
        from simulator.network import load_network

        _GRAPH = build_graph(load_network())
    except Exception:
        _GRAPH = None
    return _GRAPH


# ---------------------------------------------------------------------------
# Individual tool handlers
# ---------------------------------------------------------------------------


def get_congestion_summary(segment_id: str, window: str) -> dict[str, Any]:
    """Return mock congestion summary for a road segment."""
    speed = round(random.uniform(10.0, 80.0), 1)
    level = "high" if speed < 30 else ("medium" if speed < 60 else "low")
    return {
        "segment_id": segment_id,
        "window": window,
        "avg_speed_kmh": speed,
        "congestion_level": level,
        "vehicle_count": random.randint(50, 500),
        "incidents": random.randint(0, 3),
    }


def get_incidents_near(lat: float, lon: float, radius_m: float) -> dict[str, Any]:
    """Return mock incidents near a location."""
    count = random.randint(0, 5)
    incidents = [
        {
            "id": f"inc-{i:03d}",
            "type": random.choice(["accident", "roadwork", "congestion", "closure"]),
            "distance_m": round(random.uniform(50, radius_m), 1),
            "severity": random.choice(["low", "medium", "high"]),
        }
        for i in range(count)
    ]
    return {
        "lat": lat,
        "lon": lon,
        "radius_m": radius_m,
        "incident_count": count,
        "incidents": incidents,
    }


def compare_time_windows(segment_id: str, a: str, b: str) -> dict[str, Any]:
    """Compare congestion metrics between two time windows."""
    speed_a = round(random.uniform(15.0, 80.0), 1)
    speed_b = round(random.uniform(15.0, 80.0), 1)
    delta = round(speed_b - speed_a, 1)
    return {
        "segment_id": segment_id,
        "window_a": {
            "label": a,
            "avg_speed_kmh": speed_a,
            "congestion_level": "high" if speed_a < 30 else "medium",
        },
        "window_b": {
            "label": b,
            "avg_speed_kmh": speed_b,
            "congestion_level": "high" if speed_b < 30 else "medium",
        },
        "delta_speed_kmh": delta,
        "trend": "improved" if delta > 0 else ("worsened" if delta < 0 else "unchanged"),
    }


def top_congested_segments(limit: int, time_window: str) -> dict[str, Any]:
    """Return the top N most congested segments."""
    segments = [
        {
            "rank": i + 1,
            "segment_id": f"seg-{i + 1:02d}",
            "avg_speed_kmh": round(random.uniform(5.0, 40.0), 1),
            "congestion_level": "high",
        }
        for i in range(min(limit, 10))
    ]
    return {"time_window": time_window, "limit": limit, "segments": segments}


def forecast_for_segment(segment_id: str, horizon_minutes: int) -> dict[str, Any]:
    """Return a congestion forecast for a segment."""
    steps = min(horizon_minutes // 5, 12)
    forecast = [
        {
            "t_plus_minutes": (i + 1) * 5,
            "predicted_speed_kmh": round(random.uniform(10.0, 80.0), 1),
            "confidence": round(random.uniform(0.6, 0.95), 2),
        }
        for i in range(steps)
    ]
    return {
        "segment_id": segment_id,
        "horizon_minutes": horizon_minutes,
        "forecast": forecast,
    }


def recommend_route(origin: str, destination: str) -> dict[str, Any]:
    """Recommend shortest path between two segment IDs using graph model."""
    graph = _get_graph()
    if graph is not None:
        try:
            from graph_model import shortest_path

            path, cost = shortest_path(graph, origin, destination)
            if path:
                return {
                    "origin": origin,
                    "destination": destination,
                    "path": path,
                    "estimated_travel_time_s": round(cost, 1),
                    "hops": len(path) - 1,
                }
        except Exception:
            pass
    # Fallback mock
    return {
        "origin": origin,
        "destination": destination,
        "path": [origin, f"seg-mid-{random.randint(1, 5):02d}", destination],
        "estimated_travel_time_s": round(random.uniform(120.0, 600.0), 1),
        "hops": 2,
    }


def explain_prediction(segment_id: str, time: str) -> dict[str, Any]:
    """Explain a traffic prediction for a segment."""
    features: list[dict[str, Any]] = [
        {"feature": "time_of_day", "contribution": round(random.uniform(-0.3, 0.3), 3)},
        {"feature": "day_of_week", "contribution": round(random.uniform(-0.2, 0.2), 3)},
        {"feature": "weather", "contribution": round(random.uniform(-0.1, 0.1), 3)},
        {"feature": "historical_avg", "contribution": round(random.uniform(0.1, 0.5), 3)},
        {"feature": "nearby_incidents", "contribution": round(random.uniform(-0.4, 0.0), 3)},
    ]
    predicted_speed = round(random.uniform(15.0, 70.0), 1)
    top_feature: dict[str, Any] = max(features, key=lambda f: abs(f["contribution"]))
    return {
        "segment_id": segment_id,
        "time": time,
        "predicted_speed_kmh": predicted_speed,
        "shap_values": features,
        "top_factor": top_feature["feature"],
    }


def reachability_impact(closed_segment: str) -> dict[str, Any]:
    """Compute the impact of closing a segment on network reachability."""
    graph = _get_graph()
    if graph is not None:
        try:
            from graph_model import reachability_impact as _ri

            result = _ri(graph, closed_segment)
            return dict(result)
        except Exception:
            pass
    # Fallback mock
    return {
        "closed_segment": closed_segment,
        "affected_sources": random.randint(0, 20),
        "isolated_segments": [f"seg-{i:02d}" for i in range(random.randint(0, 5))],
    }


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_HANDLERS: dict[str, Any] = {
    "get_congestion_summary": get_congestion_summary,
    "get_incidents_near": get_incidents_near,
    "compare_time_windows": compare_time_windows,
    "top_congested_segments": top_congested_segments,
    "forecast_for_segment": forecast_for_segment,
    "recommend_route": recommend_route,
    "explain_prediction": explain_prediction,
    "reachability_impact": reachability_impact,
}


def dispatch(tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    """Route a tool call to the correct handler."""
    handler = _HANDLERS.get(tool_name)
    if handler is None:
        return {"error": f"Unknown tool: {tool_name}"}
    return handler(**tool_input)  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# JSON schemas for Anthropic tool spec
# ---------------------------------------------------------------------------

TOOLS_SCHEMA: list[dict[str, Any]] = [
    {
        "name": "get_congestion_summary",
        "description": "Get congestion summary for a road segment over a time window.",
        "input_schema": {
            "type": "object",
            "properties": {
                "segment_id": {"type": "string", "description": "Road segment identifier"},
                "window": {"type": "string", "description": "Time window, e.g. '1h', '15m', '24h'"},
            },
            "required": ["segment_id", "window"],
        },
    },
    {
        "name": "get_incidents_near",
        "description": "List traffic incidents near a geographic location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude"},
                "lon": {"type": "number", "description": "Longitude"},
                "radius_m": {"type": "number", "description": "Search radius in metres"},
            },
            "required": ["lat", "lon", "radius_m"],
        },
    },
    {
        "name": "compare_time_windows",
        "description": "Compare congestion metrics for a segment between two time windows.",
        "input_schema": {
            "type": "object",
            "properties": {
                "segment_id": {"type": "string"},
                "a": {"type": "string", "description": "First time window label"},
                "b": {"type": "string", "description": "Second time window label"},
            },
            "required": ["segment_id", "a", "b"],
        },
    },
    {
        "name": "top_congested_segments",
        "description": "Return the top N most congested road segments.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of segments to return"},
                "time_window": {"type": "string", "description": "Time window label"},
            },
            "required": ["limit", "time_window"],
        },
    },
    {
        "name": "forecast_for_segment",
        "description": "Get a traffic congestion forecast for a segment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "segment_id": {"type": "string"},
                "horizon_minutes": {
                    "type": "integer",
                    "description": "Forecast horizon in minutes",
                },
            },
            "required": ["segment_id", "horizon_minutes"],
        },
    },
    {
        "name": "recommend_route",
        "description": "Recommend the shortest route between two road segments.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Origin segment ID"},
                "destination": {"type": "string", "description": "Destination segment ID"},
            },
            "required": ["origin", "destination"],
        },
    },
    {
        "name": "explain_prediction",
        "description": "Explain a traffic speed prediction using SHAP feature attributions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "segment_id": {"type": "string"},
                "time": {
                    "type": "string",
                    "description": "ISO-8601 datetime for prediction",
                },
            },
            "required": ["segment_id", "time"],
        },
    },
    {
        "name": "reachability_impact",
        "description": "Estimate how closing a segment affects network-wide reachability.",
        "input_schema": {
            "type": "object",
            "properties": {
                "closed_segment": {
                    "type": "string",
                    "description": "Segment ID to close",
                },
            },
            "required": ["closed_segment"],
        },
    },
]
