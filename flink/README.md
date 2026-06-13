# Flink Streaming Jobs

PyFlink jobs that turn the Kafka event streams into aggregates, corroborated
incidents, and lake tables. See [`docs/data-lake.md`](../docs/data-lake.md).

| Job                   | In                              | Out                                                     |
| --------------------- | ------------------------------- | ------------------------------------------------------- |
| `windowed_speed.py`   | `traffic.raw`                   | `traffic.aggregates` (5-min tumbling avg speed/segment) |
| `cep_incidents.py`    | `traffic.raw` + `vision.events` | `alerts` (speed-drop ∧ stopped-vehicle within 60s)      |
| `kafka_to_iceberg.py` | `traffic.raw`                   | `iceberg.raw.readings` (lake raw layer)                 |

## Run

```bash
# bring up the analytics stack (Flink, Trino, MinIO bucket, Superset)
docker compose --profile analytics up -d

# submit a job (from a Flink container with PyFlink + connectors)
flink run -py flink/windowed_speed.py
```

The jobs use Flink SQL (Table API) over event-time with watermarks; the CEP job
is an interval join across the two modalities for high-confidence incidents.
