"""Tests for RAGRetriever with FakeEmbedder."""

from __future__ import annotations

import pytest

from ai_assistant.rag import FakeEmbedder, RAGRetriever


@pytest.fixture()
def retriever() -> RAGRetriever:
    return RAGRetriever(embedder=FakeEmbedder())


def test_retrieve_returns_k_results(retriever: RAGRetriever) -> None:
    results = retriever.retrieve("traffic congestion Jerusalem", k=3)
    assert len(results) == 3


def test_retrieve_returns_strings(retriever: RAGRetriever) -> None:
    results = retriever.retrieve("road incident near Malha", k=2)
    assert all(isinstance(r, str) for r in results)


def test_retrieve_k_1(retriever: RAGRetriever) -> None:
    results = retriever.retrieve("speed limit route 1", k=1)
    assert len(results) == 1


def test_retrieve_no_crash_on_empty_query(retriever: RAGRetriever) -> None:
    results = retriever.retrieve("", k=3)
    assert isinstance(results, list)
