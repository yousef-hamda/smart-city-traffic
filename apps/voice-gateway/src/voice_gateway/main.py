"""Application entrypoint: ``uvicorn voice_gateway.main:app``."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import Response

from voice_gateway import __version__
from voice_gateway.assistant_client import (
    AssistantClientBase,
    HTTPAssistantClient,
)
from voice_gateway.config import settings
from voice_gateway.logging import configure_logging
from voice_gateway.stt import STTBase, WhisperSTT
from voice_gateway.telemetry import setup_telemetry
from voice_gateway.tts import TTSBase, get_tts_client

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Module-level service singletons — overrideable for tests.
# ---------------------------------------------------------------------------
_stt: STTBase | None = None
_tts: TTSBase | None = None
_assistant: AssistantClientBase | None = None


def _get_stt() -> STTBase:
    global _stt
    if _stt is None:
        _stt = WhisperSTT(settings.whisper_model)
    return _stt


def override_stt(stt: STTBase) -> None:
    """Replace the module-level STT instance (useful in tests)."""
    global _stt
    _stt = stt


def _get_tts() -> TTSBase:
    global _tts
    if _tts is None:
        _tts = get_tts_client(settings.openai_api_key)
    return _tts


def override_tts(tts: TTSBase) -> None:
    """Replace the module-level TTS instance (useful in tests)."""
    global _tts
    _tts = tts


def _get_assistant() -> AssistantClientBase:
    global _assistant
    if _assistant is None:
        _assistant = HTTPAssistantClient(settings.ai_assistant_url)
    return _assistant


def override_assistant(assistant: AssistantClientBase) -> None:
    """Replace the module-level assistant client (useful in tests)."""
    global _assistant
    _assistant = assistant


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("service_started", port=settings.port, version=__version__)
    yield
    logger.info("service_stopped")


def create_app() -> FastAPI:
    """Build the FastAPI app; kept as a factory for tests."""
    app = FastAPI(title="Voice Gateway", version=__version__, lifespan=_lifespan)
    setup_telemetry(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name, "version": __version__}

    # ------------------------------------------------------------------
    # POST /voice/transcribe
    # ------------------------------------------------------------------
    @app.post("/voice/transcribe")
    async def transcribe(request: Request) -> dict[str, str]:
        """Accept raw audio bytes and return a JSON transcript."""
        audio_bytes = await request.body()
        text = _get_stt().transcribe(audio_bytes)
        return {"transcript": text}

    # ------------------------------------------------------------------
    # POST /voice/synthesize
    # ------------------------------------------------------------------
    @app.post("/voice/synthesize")
    async def synthesize(body: dict[str, str]) -> Response:
        """Accept JSON ``{"text": "..."}`` and return MP3 audio bytes."""
        text = body.get("text", "")
        audio_bytes = _get_tts().synthesize(text)
        return Response(content=audio_bytes, media_type="audio/mpeg")

    # ------------------------------------------------------------------
    # WebSocket /voice/stream  (full-duplex voice pipeline)
    # ------------------------------------------------------------------
    @app.websocket("/voice/stream")
    async def voice_stream(websocket: WebSocket) -> None:
        """Full-duplex WebSocket voice pipeline.

        Protocol
        --------
        Client → bytes   : raw audio chunk
        Server → text    : ``{"partial": "<transcript>"}``

        Client → text "END"  : signals that all audio has been sent
        Server → text    : ``{"final": "<transcript>"}``
        Server → text    : ``{"assistant_reply": "<reply>"}``
        Server → bytes   : synthesized MP3 audio
        Server → text    : ``{"done": true}``
        """
        await websocket.accept()
        accumulated_audio = b""

        while True:
            try:
                data = await websocket.receive()

                if data["type"] == "websocket.receive":
                    raw_bytes: bytes | None = data.get("bytes")
                    raw_text: str | None = data.get("text")

                    if raw_bytes:
                        # Audio chunk — transcribe and echo partial result.
                        accumulated_audio += raw_bytes
                        partial = _get_stt().transcribe(raw_bytes)
                        await websocket.send_text(json.dumps({"partial": partial}))

                    elif raw_text == "END":
                        # End-of-audio signal — run full pipeline.
                        final_transcript = _get_stt().transcribe(accumulated_audio)
                        await websocket.send_text(json.dumps({"final": final_transcript}))

                        assistant_reply = await _get_assistant().chat(final_transcript)
                        await websocket.send_text(
                            json.dumps({"assistant_reply": assistant_reply})
                        )

                        audio_response = _get_tts().synthesize(assistant_reply)
                        await websocket.send_bytes(audio_response)

                        await websocket.send_text(json.dumps({"done": True}))
                        break

            except Exception:
                break

        await websocket.close()

    return app


app = create_app()
