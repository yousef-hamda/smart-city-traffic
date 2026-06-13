"""Tests for POST /voice/transcribe."""

import httpx
import pytest

from voice_gateway.main import create_app, override_stt
from voice_gateway.stt import FakeSTT


@pytest.mark.asyncio
async def test_transcribe_returns_text() -> None:
    override_stt(FakeSTT())
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/voice/transcribe",
            content=b"fake audio bytes",
            headers={"Content-Type": "application/octet-stream"},
        )
    assert response.status_code == 200
    assert "transcript" in response.json()
    assert response.json()["transcript"] == "fake transcription result"
