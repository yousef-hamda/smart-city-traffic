"""Integration tests for FastAPI endpoints with mocked Anthropic."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from ai_assistant.rag import FakeEmbedder, RAGRetriever


def _make_mock_client() -> MagicMock:
    mock_client = MagicMock()
    text_response = MagicMock()
    text_response.stop_reason = "end_turn"
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Here is the traffic summary."
    text_response.content = [text_block]
    mock_client.messages.create.return_value = text_response
    return mock_client


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    mock_client = _make_mock_client()
    fake_rag = RAGRetriever(embedder=FakeEmbedder())

    from ai_assistant.main import create_app

    app = create_app(anthropic_client=mock_client, rag=fake_rag)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_returns_200_with_reply() -> None:
    mock_client = _make_mock_client()
    fake_rag = RAGRetriever(embedder=FakeEmbedder())

    from ai_assistant.main import create_app

    app = create_app(anthropic_client=mock_client, rag=fake_rag)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/chat", json={"message": "What is traffic like on route 1?"})

    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert isinstance(body["reply"], str)


@pytest.mark.asyncio
async def test_chat_stream_returns_event_stream() -> None:
    mock_client = _make_mock_client()
    fake_rag = RAGRetriever(embedder=FakeEmbedder())

    from ai_assistant.main import create_app

    app = create_app(anthropic_client=mock_client, rag=fake_rag)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/chat/stream",
            json={"message": "traffic near Malha"},
        )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_chat_off_topic_returns_refusal() -> None:
    mock_client = _make_mock_client()
    fake_rag = RAGRetriever(embedder=FakeEmbedder())

    from ai_assistant.main import create_app

    app = create_app(anthropic_client=mock_client, rag=fake_rag)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/chat", json={"message": "what is the best football team?"})

    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    # Should not call the Anthropic API
    mock_client.messages.create.assert_not_called()
