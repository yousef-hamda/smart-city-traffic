"""RAG retrieval using ChromaDB + sentence-transformers (or FakeEmbedder for tests)."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    pass

DOCS_DIR = Path(__file__).parent / "docs"

# Chunk size in characters
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80


class Embedder(Protocol):
    """Minimal interface for an embedding model."""

    def encode(self, texts: list[str], **kwargs: Any) -> Any:
        """Return an array-like of float vectors, one per text."""
        ...


class FakeEmbedder:
    """Deterministic random embedder used in tests (no model download)."""

    DIM = 384

    def encode(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        import random

        rng = random.Random(42)
        return [[rng.gauss(0, 1) for _ in range(self.DIM)] for _ in texts]


def _load_real_embedder() -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2")


def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if c]


def _load_docs() -> list[tuple[str, str]]:
    """Return [(chunk_text, source_filename), ...] for all docs."""
    pairs: list[tuple[str, str]] = []
    for path in sorted(DOCS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        for chunk in _chunk_text(text):
            pairs.append((chunk, path.name))
    return pairs


class RAGRetriever:
    """Embed docs corpus and retrieve relevant chunks for a query."""

    def __init__(self, embedder: Embedder | None = None) -> None:
        import chromadb

        self._embedder: Embedder = embedder if embedder is not None else _load_real_embedder()
        self._client = chromadb.EphemeralClient()
        collection_name = f"traffic_docs_{uuid.uuid4().hex[:8]}"
        self._collection = self._client.create_collection(collection_name)
        self._index_docs()

    def _index_docs(self) -> None:
        docs = _load_docs()
        if not docs:
            return
        texts = [d[0] for d in docs]
        sources = [d[1] for d in docs]
        embeddings = self._embedder.encode(texts, show_progress_bar=False)
        # Convert to plain Python list-of-lists
        vecs = [list(map(float, row)) for row in embeddings]
        ids = [f"doc-{i}" for i in range(len(texts))]
        self._collection.add(
            documents=texts,
            embeddings=vecs,  # type: ignore[arg-type]
            metadatas=[{"source": s} for s in sources],
            ids=ids,
        )

    def retrieve(self, query: str, k: int = 3) -> list[str]:
        """Return the k most relevant text chunks for a query."""
        n_docs = self._collection.count()
        if n_docs == 0:
            return []
        k_actual = min(k, n_docs)
        q_vec = list(map(float, self._embedder.encode([query], show_progress_bar=False)[0]))
        results = self._collection.query(query_embeddings=[q_vec], n_results=k_actual)  # type: ignore[arg-type]
        docs_list: list[str] = results["documents"][0] if results["documents"] else []
        return docs_list
