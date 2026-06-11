# Camera Simulator

Renders synthetic traffic-camera frames with OpenCV and publishes them via RTSP / Kafka. Lands in Phase 3.

> **Phase 1 skeleton.** The CLI surface is final; generation logic arrives in
> the phase noted above.

## Usage

```bash
python -m camera_simulator run --help
```

## Environment

| Variable | Purpose |
|---|---|
| `KAFKA_BOOTSTRAP_SERVERS` | localhost:29092 |


## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q && ruff check src tests && mypy src
```
