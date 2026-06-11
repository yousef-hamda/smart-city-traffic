# Sensor Simulator

Generates realistic Jerusalem-area traffic sensor events (rush-hour curves, incidents) over MQTT + HTTP. Lands in Phase 2.

> **Phase 1 skeleton.** The CLI surface is final; generation logic arrives in
> the phase noted above.

## Usage

```bash
python -m simulator run --help
```

## Environment

| Variable | Purpose |
|---|---|
| `INGESTION_HTTP_URL` | http://localhost:8081 |
| `MQTT_BROKER_HOST` | localhost |


## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q && ruff check src tests && mypy src
```
