"""Tests for POST /voice/synthesize."""

import httpx
import pytest

from voice_gateway.main import create_app, override_tts
from voice_gateway.tts import FakeTTS


@pytest.mark.asyncio
async def test_synthesize_returns_audio() -> None:
    override_tts(FakeTTS())
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/voice/synthesize",
            json={"text": "Hello world"},
        )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert len(response.content) > 0
