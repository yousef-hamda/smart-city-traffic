import httpx
import pytest

from rl_optimizer.main import create_app
from rl_optimizer.recommend import ApproachState, IntersectionState, recommend


def _state() -> list[IntersectionState]:
    return [
        IntersectionState(
            name="J0",
            approaches=[
                ApproachState("N", 2.0),
                ApproachState("E", 25.0),
                ApproachState("S", 3.0),
                ApproachState("W", 22.0),
            ],
            phases=[[0, 2], [1, 3]],
            current_phase=0,
        )
    ]


def test_recommend_picks_high_pressure_phase() -> None:
    (rec,) = recommend(_state())
    assert rec["intersection"] == "J0"
    assert rec["recommended_phase"] == 1  # EW is the loaded direction
    assert int(rec["green_seconds"]) > 0


@pytest.mark.asyncio
async def test_recommend_endpoint() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    payload = {
        "intersections": [
            {
                "name": "J0",
                "approaches": [
                    {"name": "N", "queue": 2.0},
                    {"name": "E", "queue": 25.0},
                    {"name": "S", "queue": 3.0},
                    {"name": "W", "queue": 22.0},
                ],
                "phases": [[0, 2], [1, 3]],
                "current_phase": 0,
            }
        ]
    }
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/health")
        resp = await client.post("/recommend/signal-timing", json=payload)
    assert health.status_code == 200
    body = resp.json()
    assert resp.status_code == 200
    assert body["recommendations"][0]["recommended_phase"] == 1
