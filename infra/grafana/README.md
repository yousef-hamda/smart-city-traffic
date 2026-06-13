# Observability

OpenTelemetry in every service feeds the three pillars, correlated in Grafana.

```
services ──OTLP──► Tempo (traces)        ┐
         ──/metrics─► Prometheus (metrics) ├─► Grafana (dashboards + alerts)
         ──stdout JSON─► Loki (logs)       ┘
                          Prometheus ──► Alertmanager (routing)
```

Bring it up: `docker compose --profile observability up -d`

| Tool         | URL (dev)             | Purpose                              |
| ------------ | --------------------- | ------------------------------------ |
| Grafana      | http://localhost:3030 | dashboards, explore, trace↔log links |
| Prometheus   | http://localhost:9090 | metrics + alert rules                |
| Alertmanager | http://localhost:9095 | alert routing                        |
| Tempo        | :3200 / OTLP :4317    | distributed traces                   |
| Loki         | http://localhost:3100 | logs                                 |

## Correlation

Every service's structured JSON logs carry `trace_id`/`span_id` from the active
OTel span. In Grafana, a Loki log line's `trace_id` is a clickable link into
the Tempo trace (derived field); a Tempo span links back to its logs
(`tracesToLogsV2`). Trace context propagates across the polyglot path
(Java → Kafka → Python → gRPC → Node → browser), so one request is followable
end to end.

## Dashboards (`infra/grafana/dashboards/`)

- **Platform Overview** — services up, request rate, p95 latency, 5xx ratio,
  memory/CPU.
- **Traffic KPIs** — ingest/reject rates, vision throughput, active incidents,
  prediction freshness.

Provisioned automatically (`provisioning/`). Add JSON files here and they load
on restart.

## Alerts

- `prometheus/alerts.yml` — availability, latency, Kafka lag, prediction
  staleness.
- `prometheus/slo_alerts.yml` — multi-window error-budget **burn-rate** alerts
  for the API availability SLO (see [`docs/runbooks/slos.md`](../../docs/runbooks/slos.md)).
