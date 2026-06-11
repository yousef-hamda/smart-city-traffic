# Vision Service

Consumes camera frames from Kafka and runs YOLOv8 detection + ByteTrack tracking. Implementation lands in Phase 3.

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
| `PORT` | `8082` | HTTP listen port |
| `LOG_LEVEL` | `INFO` | structlog level |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _unset_ | OTLP gRPC endpoint; tracing disabled when unset |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:29092` | service-specific |
| `REDIS_URL` | `redis://localhost:6379/0` | service-specific |


## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn vision_service.main:app --reload --port 8082
```

## Tests & quality

```bash
pytest -q
ruff check src tests && mypy src
```

## Observability

JSON logs to stdout (one object per line, `trace_id`/`span_id` correlated);
OTLP traces to Tempo when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
