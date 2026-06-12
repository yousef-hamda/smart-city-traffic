import httpx
import pytest

from vision_service.main import create_app
from vision_service.snapshots import SnapshotStore


@pytest.mark.asyncio
async def test_health() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "vision-service"


@pytest.mark.asyncio
async def test_snapshot_404_when_absent() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/snapshot/unknown-segment")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_snapshot_returns_png_when_present() -> None:
    app = create_app()
    store: SnapshotStore = app.state.snapshots
    store.put("jaffa-road-00", 1, b"\x89PNG\r\n\x1a\nfake")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/snapshot/jaffa-road-00")
        segments = await client.get("/segments")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert "jaffa-road-00" in segments.json()["segments"]
