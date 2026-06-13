"""Integration tests for REST API endpoints."""
from __future__ import annotations

import httpx
import pytest
from asgi_lifespan import LifespanManager  # type: ignore[import-untyped]


@pytest.mark.asyncio
async def test_health_returns_ok() -> None:
    from ml_prediction.main import create_app

    app = create_app()
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "ml-prediction"
    assert body["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_forecast_demand_endpoint() -> None:
    from ml_prediction.main import create_app

    app = create_app()
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/forecast/demand",
                json={"segment_id": "jaffa-road-00", "horizon_hours": 3},
            )
    assert response.status_code == 200
    body = response.json()
    assert "predictions" in body
    assert "model_version" in body
    assert len(body["predictions"]) == 3
    assert isinstance(body["model_version"], str)
    assert len(body["model_version"]) > 0
    for p in body["predictions"]:
        assert "hour" in p
        assert "vehicle_count" in p


@pytest.mark.asyncio
async def test_detect_anomaly_endpoint() -> None:
    from ml_prediction.main import create_app

    app = create_app()
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/detect/anomaly",
                json={"segment_id": "jaffa-road-00"},
            )
    assert response.status_code == 200
    body = response.json()
    assert "is_anomaly" in body
    assert "score" in body
    assert "model_version" in body
    assert isinstance(body["is_anomaly"], bool)
    assert isinstance(body["score"], float)


@pytest.mark.asyncio
async def test_predict_congestion_endpoint() -> None:
    from ml_prediction.main import create_app

    app = create_app()
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/predict/congestion",
                json={"segment_id": "jaffa-road-00", "horizon_minutes": 30},
            )
    assert response.status_code == 200
    body = response.json()
    assert "predicted_speed_kmh" in body
    assert "lower_ci" in body
    assert "upper_ci" in body
    assert "shap_top5" in body
    assert "model_version" in body
    assert len(body["shap_top5"]) == 5
    for item in body["shap_top5"]:
        assert "feature" in item
        assert "value" in item


@pytest.mark.asyncio
async def test_detect_anomaly_with_readings() -> None:
    from ml_prediction.main import create_app

    app = create_app()
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/detect/anomaly",
                json={
                    "segment_id": "jaffa-road-00",
                    "readings": [
                        {"speed": 50.0, "occupancy": 30.0, "count": 100.0},
                        {"speed": 45.0, "occupancy": 35.0, "count": 110.0},
                    ],
                },
            )
    assert response.status_code == 200
    body = response.json()
    assert "is_anomaly" in body
