# dbt — lake transformations

Builds staging views and materialized marts on the Iceberg lake via Trino
(`dbt-trino`).

```bash
pip install dbt-trino
export DBT_PROFILES_DIR=$PWD          # uses ./profiles.yml
cd analytics/dbt
dbt deps && dbt run && dbt test
```

- `models/staging/stg_readings.sql` — typed, cleaned readings.
- `models/marts/mart_segment_hourly.sql` — hourly fact table (BI backbone).
- `models/marts/mart_incident_impact.sql` — slowdown vs segment baseline.
- `models/marts/mart_carbon_savings.sql` — CO₂ saved by RL vs fixed-time signals.

Trino must be reachable (`TRINO_HOST`/`TRINO_PORT`, default localhost:8090 in
compose → container 8080) with the `iceberg` catalog configured.
