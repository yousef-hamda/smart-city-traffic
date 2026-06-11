# Federated Learning Coordinator

Flower coordinator orchestrating privacy-preserving training rounds across simulated sensor clusters. Lands in Phase 8.

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
| `PORT` | `8085` | HTTP listen port |
| `LOG_LEVEL` | `INFO` | structlog level |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _unset_ | OTLP gRPC endpoint; tracing disabled when unset |


## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn federated_coordinator.main:app --reload --port 8085
```

## Tests & quality

```bash
pytest -q
ruff check src tests && mypy src
```

## Observability

JSON logs to stdout (one object per line, `trace_id`/`span_id` correlated);
OTLP traces to Tempo when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
