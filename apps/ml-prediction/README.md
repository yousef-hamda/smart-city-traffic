# ML Prediction Service

Serves congestion (LSTM), anomaly (Isolation Forest) and demand (XGBoost) models over REST + gRPC. Models land in Phases 5-6.

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
| `PORT` | `8083` | HTTP listen port |
| `LOG_LEVEL` | `INFO` | structlog level |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _unset_ | OTLP gRPC endpoint; tracing disabled when unset |
| `POSTGRES_DSN` | `postgresql://traffic:traffic_dev_password@localhost:5432/traffic` | service-specific |
| `REDIS_URL` | `redis://localhost:6379/1` | service-specific |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | service-specific |


## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn ml_prediction.main:app --reload --port 8083
```

## Tests & quality

```bash
pytest -q
ruff check src tests && mypy src
```

## Observability

JSON logs to stdout (one object per line, `trace_id`/`span_id` correlated);
OTLP traces to Tempo when `OTEL_EXPORTER_OTLP_ENDPOINT` is set.
