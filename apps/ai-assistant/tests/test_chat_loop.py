"""Tests for the Anthropic chat loop logic in main.py."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ai_assistant.rag import FakeEmbedder, RAGRetriever


@pytest.fixture()
def fake_rag() -> RAGRetriever:
    return RAGRetriever(embedder=FakeEmbedder())


def _make_mock_client() -> MagicMock:
    mock_client = MagicMock()

    # First call: tool_use response
    tool_use_response = MagicMock()
    tool_use_response.stop_reason = "tool_use"
    tool_use_block = MagicMock()
    tool_use_block.type = "tool_use"
    tool_use_block.id = "tool_123"
    tool_use_block.name = "get_congestion_summary"
    tool_use_block.input = {"segment_id": "seg-01", "window": "1h"}
    tool_use_response.content = [tool_use_block]

    # Second call: final text
    text_response = MagicMock()
    text_response.stop_reason = "end_turn"
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Traffic is congested."
    text_response.content = [text_block]

    mock_client.messages.create.side_effect = [tool_use_response, text_response]
    return mock_client


def test_chat_loop_executes_two_turns(fake_rag: RAGRetriever) -> None:
    from ai_assistant.main import _run_chat_loop

    mock_client = _make_mock_client()
    reply, tool_calls = _run_chat_loop(
        client=mock_client,
        message="What is the traffic on segment seg-01?",
        rag=fake_rag,
    )

    assert reply == "Traffic is congested."
    assert mock_client.messages.create.call_count == 2


def test_chat_loop_dispatches_tool(fake_rag: RAGRetriever) -> None:
    from ai_assistant.main import _run_chat_loop

    mock_client = _make_mock_client()
    reply, tool_calls = _run_chat_loop(
        client=mock_client,
        message="What is the traffic on segment seg-01?",
        rag=fake_rag,
    )

    assert "get_congestion_summary" in tool_calls


def test_chat_loop_returns_text(fake_rag: RAGRetriever) -> None:
    from ai_assistant.main import _run_chat_loop

    mock_client = _make_mock_client()
    reply, _ = _run_chat_loop(
        client=mock_client,
        message="Summarize current traffic",
        rag=fake_rag,
    )

    assert isinstance(reply, str)
    assert len(reply) > 0
