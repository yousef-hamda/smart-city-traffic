"""Tests for tool handlers and dispatch."""

from __future__ import annotations

from ai_assistant.tools import (
    TOOLS_SCHEMA,
    compare_time_windows,
    dispatch,
    explain_prediction,
    forecast_for_segment,
    get_congestion_summary,
    get_incidents_near,
    reachability_impact,
    recommend_route,
    top_congested_segments,
)


def test_get_congestion_summary_keys() -> None:
    result = get_congestion_summary("seg-01", "1h")
    assert "segment_id" in result
    assert "congestion_level" in result
    assert "avg_speed_kmh" in result
    assert result["segment_id"] == "seg-01"


def test_get_incidents_near_keys() -> None:
    result = get_incidents_near(31.77, 35.21, 500.0)
    assert "incident_count" in result
    assert "incidents" in result
    assert isinstance(result["incidents"], list)


def test_compare_time_windows_keys() -> None:
    result = compare_time_windows("seg-01", "morning", "evening")
    assert "window_a" in result
    assert "window_b" in result
    assert "delta_speed_kmh" in result
    assert "trend" in result


def test_top_congested_segments_keys() -> None:
    result = top_congested_segments(5, "1h")
    assert "segments" in result
    assert len(result["segments"]) == 5
    assert result["segments"][0]["rank"] == 1


def test_forecast_for_segment_keys() -> None:
    result = forecast_for_segment("seg-01", 30)
    assert "forecast" in result
    assert len(result["forecast"]) == 6  # 30 / 5


def test_recommend_route_keys() -> None:
    result = recommend_route("seg-01", "seg-05")
    assert "path" in result
    assert "estimated_travel_time_s" in result
    assert isinstance(result["path"], list)
    assert len(result["path"]) >= 2


def test_explain_prediction_keys() -> None:
    result = explain_prediction("seg-01", "2024-06-01T08:00:00")
    assert "shap_values" in result
    assert "top_factor" in result
    assert isinstance(result["shap_values"], list)


def test_reachability_impact_keys() -> None:
    result = reachability_impact("seg-01")
    assert "closed_segment" in result
    assert "isolated_segments" in result


def test_dispatch_routes_correctly() -> None:
    result = dispatch("get_congestion_summary", {"segment_id": "seg-02", "window": "30m"})
    assert result["segment_id"] == "seg-02"


def test_dispatch_unknown_tool() -> None:
    result = dispatch("nonexistent_tool", {})
    assert "error" in result


def test_tools_schema_count() -> None:
    assert len(TOOLS_SCHEMA) == 8


def test_tools_schema_structure() -> None:
    for tool in TOOLS_SCHEMA:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
