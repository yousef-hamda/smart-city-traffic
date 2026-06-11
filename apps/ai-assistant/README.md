# AI Assistant Service

Claude-powered traffic assistant with tool-calling and RAG over operational docs. Lands in Phase 13.

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
| `PORT` | `8086` | HTTP listen port |
| `LOG_LEVEL` | `INFO` | structlog level |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _unset_ | OTLP gRPC endpoint; tracing disabled when unset |
| `ANTHROPIC_API_KEY` | `` | service-specific |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6` | service-specific |
| `POSTGRES_DSN` | `postgresql://traffic:traffic_dev_password@localhost:5432/traffic` | service-specific |
| `NEO4J_URI` | `bolt://localhost:7687` | service-specific |
| `NEO4J_PASSWORD` | `` | service-specific |


## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn ai_assistant.main:app --reload --port 8086
```

## Tests & quality

```bash
pytest -q
ruff check src tests && mypy src
```

## Observability

JSON logs to stdout (one object per line, `trace_id`/`span_id` correlated);
OTLP traces to Tempo when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
