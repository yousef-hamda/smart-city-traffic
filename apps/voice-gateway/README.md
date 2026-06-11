# Voice Gateway

Whisper STT + TTS + duplex voice WebSocket bridging into the AI assistant. Lands in Phase 13.

> **Phase 1 skeleton.** This service currently boots, reports `/health`, emits
> structured JSON logs, and exports OTel traces when configured. The full
> implementation arrives in the phase noted above.

## Interfaces

| Kind | Endpoint | Status |
|---|---|---|
| REST | `GET /health` | ✅ implemented |

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `8087` | HTTP listen port |
| `LOG_LEVEL` | `INFO` | structlog level |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _unset_ | OTLP gRPC endpoint; tracing disabled when unset |
| `AI_ASSISTANT_URL` | `http://localhost:8086` | service-specific |
| `OPENAI_API_KEY` | `` | service-specific |
| `ELEVENLABS_API_KEY` | `` | service-specific |


## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn voice_gateway.main:app --reload --port 8087
```

## Tests & quality

```bash
pytest -q
ruff check src tests && mypy src
```

## Observability

JSON logs to stdout (one object per line, `trace_id`/`span_id` correlated);
OTLP traces to Tempo when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
