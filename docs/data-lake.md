# Data Lake & Analytics

The modern data stack that turns the Kafka event streams into governed,
queryable tables and BI dashboards.

```
Kafka ──Flink──► Iceberg tables (MinIO)  ──Trino──►  dbt models  ──►  Superset
 traffic.raw     raw.readings              SQL on    staging → marts    dashboards
 vision.events   raw.vision_events         the lake
```

## Streaming (Apache Flink)

`flink/` holds three PyFlink jobs:

| Job                   | Purpose                                                  | Out                  |
| --------------------- | -------------------------------------------------------- | -------------------- |
| `windowed_speed.py`   | 5-min tumbling avg speed per segment                     | `traffic.aggregates` |
| `cep_incidents.py`    | correlate speed-drop + camera stopped-vehicle within 60s | `alerts`             |
| `kafka_to_iceberg.py` | land raw streams into the lake                           | `iceberg.raw.*`      |

`cep_incidents` is the high-value one: requiring _both_ a speed drop and a
camera-detected stopped vehicle on the same segment within a minute yields
far fewer false positives than either signal alone.

## Lakehouse (MinIO + Iceberg + Trino)

- **MinIO** is the S3-compatible object store (`traffic-lake` bucket).
- **Apache Iceberg** tables give the lake ACID writes, schema evolution, and
  time travel over object storage (see [ADR 0004](adr/0004-iceberg-for-lake.md)).
- **Trino** queries Iceberg via the catalog in
  `infra/trino/catalog/iceberg.properties`; it's the SQL engine for both dbt
  and Superset.

## Transformations (dbt-trino)

`analytics/dbt/` is a dbt project that builds, all through Trino:

- **staging** (`stg_readings`) — typed, cleaned views over `raw.readings`.
- **marts** (materialized tables):
  - `mart_segment_hourly` — hourly speed/occupancy/congestion per segment (the
    BI backbone).
  - `mart_incident_impact` — per segment-hour slowdown vs the segment baseline.
  - `mart_carbon_savings` — estimated CO₂ saved by RL signal timing vs
    fixed-time, using the measured ~30% wait reduction from
    [docs/rl.md](rl.md). Assumptions are documented inline and tunable.

```bash
cd analytics/dbt && dbt deps && dbt run && dbt test
```

## BI (Apache Superset)

`analytics/superset/dashboards/` holds four importable dashboard exports:
**Executive Overview**, **Segment Performance**, **Incident Analysis**, and
**Carbon Impact** — each built on the dbt marts.

```bash
superset import-dashboards -p analytics/superset/dashboards/executive_overview.yaml
```
