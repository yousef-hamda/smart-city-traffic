import httpx
import pytest

from federated_coordinator.main import create_app


@pytest.mark.asyncio
async def test_health() -> None:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "federated-coordinator"


@pytest.mark.asyncio
async def test_train_and_report() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        empty = await client.get("/report")
        assert empty.json()["status"] == "no_run_yet"

        trained = await client.post("/train/federated", json={"rounds": 8, "local_epochs": 2})
        body = trained.json()
        assert trained.status_code == 200
        assert body["clients"] == 5
        assert "federated_mse" in body

        report = await client.get("/report")
        assert report.json()["federated_mse"] == body["federated_mse"]
