# Voice Gateway

Whisper STT + TTS + full-duplex voice WebSocket bridging into the AI assistant.
Part of Phase 13 of the Smart City Traffic platform.

## Endpoints

| Kind      | Endpoint                 | Description                                |
| --------- | ------------------------ | ------------------------------------------ |
| REST      | `GET /health`            | Liveness check — returns `{"status":"ok"}` |
| REST      | `POST /voice/transcribe` | Transcribe raw audio bytes to text         |
| REST      | `POST /voice/synthesize` | Synthesize text to MP3 audio               |
| WebSocket | `WS /voice/stream`       | Full-duplex voice pipeline                 |

### POST /voice/transcribe

- **Request**: raw audio bytes, `Content-Type: application/octet-stream`
- **Response**: `{"transcript": "<text>"}`

Uses faster-whisper running on CPU with int8 quantization. The model is
lazy-loaded on the first request so the service starts instantly and
tests never trigger a download.

### POST /voice/synthesize

- **Request**: `{"text": "Hello world"}`
- **Response**: MP3 audio bytes, `Content-Type: audio/mpeg`

Backed by `OpenAITTS` when `OPENAI_API_KEY` is set; falls back to
`OfflineTTS` (placeholder MP3) when no key is configured.

### WebSocket /voice/stream

Full-duplex protocol:

```
Client -> bytes   : raw audio chunk
Server <- text    : {"partial": "<transcript>"}

Client -> bytes   : more audio ...
Server <- text    : {"partial": "<transcript>"}

Client -> text "END"
Server <- text    : {"final": "<full transcript>"}
Server <- text    : {"assistant_reply": "<reply from AI assistant>"}
Server <- bytes   : synthesized MP3 of the reply
Server <- text    : {"done": true}
```

Each audio chunk is individually transcribed (for low-latency partial
feedback). When the client sends `"END"`, the accumulated audio is
transcribed once more for a clean final result, forwarded to the AI
assistant service, and the reply is spoken back as MP3.

## Architecture — Lazy STT and Mockable Backends

All three backends (STT, TTS, AssistantClient) are held as module-level
singletons and can be replaced at import time for tests:

```python
from voice_gateway.main import override_stt, override_tts, override_assistant
from voice_gateway.stt import FakeSTT
from voice_gateway.tts import FakeTTS
from voice_gateway.assistant_client import FakeAssistantClient

override_stt(FakeSTT())
override_tts(FakeTTS())
override_assistant(FakeAssistantClient())
```

The `WhisperSTT` model is lazy-loaded inside `_get_model()` so pytest
never triggers a Whisper model download at import time.

## Offline TTS Approach

When `OPENAI_API_KEY` is empty, `OfflineTTS` returns a minimal silent
MP3 placeholder (`b"ID3" + b"\x00" * 100`). This keeps the service
deployable in air-gapped or cost-sensitive environments while the API
surface stays identical. A pyttsx3-based implementation can be swapped
in by subclassing `TTSBase` and calling `override_tts()`.

## Environment Variables

| Variable                      | Default                 | Purpose                                                  |
| ----------------------------- | ----------------------- | -------------------------------------------------------- |
| `PORT`                        | `8087`                  | HTTP listen port                                         |
| `LOG_LEVEL`                   | `INFO`                  | structlog level                                          |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _unset_                 | OTLP gRPC endpoint; tracing disabled when unset          |
| `AI_ASSISTANT_URL`            | `http://localhost:8086` | Base URL of the AI assistant service                     |
| `OPENAI_API_KEY`              | ``                      | Enables OpenAI TTS when set                              |
| `ELEVENLABS_API_KEY`          | ``                      | Reserved for ElevenLabs TTS integration                  |
| `WHISPER_MODEL`               | `tiny`                  | faster-whisper model size (tiny/base/small/medium/large) |

## Development

```bash
# Create venv and install with dev extras
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Start the service
uvicorn voice_gateway.main:app --reload --port 8087
```

## Tests

```bash
pytest apps/voice-gateway/tests/ -q
```

All tests use fake backends — no model downloads, no network calls.

## Code Quality

```bash
ruff check src tests
mypy src
```

## Observability

JSON logs to stdout (one object per line, `trace_id`/`span_id` correlated
when an OTel span is active); OTLP traces exported to Tempo when
`OTEL_EXPORTER_OTLP_ENDPOINT` is set.
