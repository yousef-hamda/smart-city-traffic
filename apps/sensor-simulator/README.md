# Sensor Simulator

Generates realistic Jerusalem-area traffic sensor telemetry. This is a
**simulator and says so** — the engineering value of the platform is the
system around it, not the data source.

## What it models

- **Israeli weekly rhythm** — Sun–Thu bimodal commute peaks (≈08:00 and
  ≈17:30), Friday's single pre-Shabbat late-morning peak that collapses in
  the afternoon, Saturday quiet until Shabbat ends in the evening.
- **Hotspots** — gaussian demand bumps around configured POIs
  (`config/jerusalem.yaml`: Mahane Yehuda, the Central Bus Station, the Old
  City gates…).
- **Fundamental diagram** — speed falls concavely as occupancy saturates;
  noise via lognormal demand jitter and Poisson vehicle counts.
- **Incidents** — Poisson random arrivals (configurable rate) or manual
  injection; an incident cuts segment capacity to 35% and the model turns
  that into visible speed collapse.
- **Network** — segments/sensors/cameras derived deterministically from
  [`scripts/seed/data/jerusalem_roads.json`](../../scripts/seed/data/jerusalem_roads.json)
  via `simulator.network`, the same module the database seed uses, so IDs
  always match what's in Postgres.

## Usage

```bash
# NDJSON to stdout (no infrastructure needed)
python -m simulator run --rate 50 --hotspots config/jerusalem.yaml --stdout

# Against the local stack: MQTT device messages + HTTP bulk batches
python -m simulator run --mqtt-host localhost --http-url http://localhost:8081

# Deterministic burst (tests, demos)
python -m simulator run --rate 500 --duration 10 --seed 42 --stdout

# Replay the canned rush-hour accident scenario
python -m simulator replay --file ../../ml/data/scenarios/rush_hour_accident.csv --speedup 10
```

Event contract (one JSON object per reading):

```json
{
  "sensor_id": "S-jaffa-road-02-1",
  "ts": "2026-06-08T08:00:00+03:00",
  "lat": 31.781,
  "lon": 35.218,
  "vehicle_count": 11,
  "avg_speed_kmh": 31.4,
  "occupancy_pct": 38.2
}
```

## Environment

| Variable             | Purpose                   |
| -------------------- | ------------------------- |
| `INGESTION_HTTP_URL` | default for `--http-url`  |
| `MQTT_BROKER_HOST`   | default for `--mqtt-host` |

## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q && ruff check src tests && mypy src
```
