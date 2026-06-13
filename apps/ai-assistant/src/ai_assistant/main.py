"""Application entrypoint: ``uvicorn ai_assistant.main:app``."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import anthropic
import structlog
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ai_assistant import __version__
from ai_assistant.config import settings
from ai_assistant.guardrails import get_refusal_message, is_off_topic
from ai_assistant.language import detect_language
from ai_assistant.logging import configure_logging
from ai_assistant.rag import RAGRetriever
from ai_assistant.telemetry import setup_telemetry
from ai_assistant.tools import TOOLS_SCHEMA, dispatch

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# RAG singleton (lazy)
# ---------------------------------------------------------------------------
_rag: RAGRetriever | None = None


def _get_rag() -> RAGRetriever:
    global _rag
    if _rag is None:
        _rag = RAGRetriever()
    return _rag


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    tool_calls_made: list[str]


# ---------------------------------------------------------------------------
# Anthropic client factory (injectable for tests)
# ---------------------------------------------------------------------------


def _make_anthropic_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _build_system_prompt(context_chunks: list[str], lang: str) -> str:
    lang_instruction = {
        "he": "Please respond in Hebrew.",
        "ar": "Please respond in Arabic.",
        "en": "Please respond in English.",
    }.get(lang, "Please respond in English.")

    context_text = (
        "\n\n---\n\n".join(context_chunks) if context_chunks else "No additional context available."
    )
    return (
        "You are the Jerusalem Smart City Traffic Assistant. "
        "You help traffic operators and citizens understand road conditions, incidents, "
        "and route recommendations in Jerusalem. "
        "Use the provided tools to answer questions about real-time and historical "
        "traffic data.\n\n"
        f"## Relevant operational context\n\n{context_text}\n\n"
        f"## Language instruction\n{lang_instruction}"
    )


def _run_chat_loop(
    client: anthropic.Anthropic,
    message: str,
    rag: RAGRetriever,
) -> tuple[str, list[str]]:
    """Synchronous Anthropic tool-calling loop. Returns (reply, tool_names_used)."""
    lang = detect_language(message)
    context_chunks = rag.retrieve(message, k=3)
    system_prompt = _build_system_prompt(context_chunks, lang)

    messages: list[dict[str, Any]] = [{"role": "user", "content": message}]
    tool_calls_made: list[str] = []

    while True:
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,  # type: ignore[arg-type]
            tools=TOOLS_SCHEMA,  # type: ignore[arg-type]
        )

        if response.stop_reason == "tool_use":
            # Collect all tool results
            tool_results: list[dict[str, Any]] = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made.append(block.name)
                    result = dispatch(block.name, dict(block.input))
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                        }
                    )
            # Append assistant turn + tool results
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # end_turn or stop_sequence — extract text
            reply = ""
            for block in response.content:
                if block.type == "text":
                    reply = block.text
                    break
            return reply, tool_calls_made


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("service_started", port=settings.port, version=__version__)
    yield
    logger.info("service_stopped")


def create_app(
    anthropic_client: anthropic.Anthropic | None = None,
    rag: RAGRetriever | None = None,
) -> FastAPI:
    """Build the FastAPI app; kept as a factory for tests."""
    app = FastAPI(title="AI Assistant Service", version=__version__, lifespan=_lifespan)
    setup_telemetry(app)

    # Resolve dependencies
    def _client() -> anthropic.Anthropic:
        return anthropic_client if anthropic_client is not None else _make_anthropic_client()

    def _rag_dep() -> RAGRetriever:
        return rag if rag is not None else _get_rag()

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name, "version": __version__}

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        if is_off_topic(request.message):
            lang = detect_language(request.message)
            return ChatResponse(reply=get_refusal_message(lang), tool_calls_made=[])

        reply, tool_calls_made = _run_chat_loop(
            client=_client(),
            message=request.message,
            rag=_rag_dep(),
        )
        return ChatResponse(reply=reply, tool_calls_made=tool_calls_made)

    @app.post("/chat/stream")
    async def chat_stream(request: ChatRequest) -> StreamingResponse:
        if is_off_topic(request.message):
            lang = detect_language(request.message)
            refusal = get_refusal_message(lang)

            async def _refusal_gen() -> AsyncGenerator[str, None]:
                yield f"data: {refusal}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(_refusal_gen(), media_type="text/event-stream")

        lang = detect_language(request.message)
        context_chunks = _rag_dep().retrieve(request.message, k=3)
        system_prompt = _build_system_prompt(context_chunks, lang)

        client = _client()
        messages: list[dict[str, Any]] = [{"role": "user", "content": request.message}]
        tool_calls_made: list[str] = []

        # Run tool loop synchronously before streaming final reply
        reply_text = ""
        while True:
            response = client.messages.create(
                model=settings.anthropic_model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages,  # type: ignore[arg-type]
                tools=TOOLS_SCHEMA,  # type: ignore[arg-type]
            )
            if response.stop_reason == "tool_use":
                tool_results_stream: list[dict[str, Any]] = []
                for block in response.content:
                    if block.type == "tool_use":
                        tool_calls_made.append(block.name)
                        result = dispatch(block.name, dict(block.input))
                        tool_results_stream.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result),
                            }
                        )
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results_stream})
            else:
                # Stream final text word by word
                for block in response.content:
                    if block.type == "text":
                        reply_text = block.text
                        break
                break

        async def _stream_gen() -> AsyncGenerator[str, None]:
            words = reply_text.split()
            for word in words:
                yield f"data: {word} \n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(_stream_gen(), media_type="text/event-stream")

    return app


app = create_app()
