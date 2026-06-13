# Service Level Objectives

The promises we make and how we measure them. Burn-rate alerts
(`infra/prometheus/slo_alerts.yml`) page before the budget is gone.

## SLOs

| Service / journey        | SLI                                  | SLO (30-day)            | Error budget   |
| ------------------------ | ------------------------------------ | ----------------------- | -------------- |
| API gateway availability | % non-5xx responses                  | **99.9%**               | 43.2 min/month |
| API gateway latency      | % requests < 300 ms                  | 99%                     | —              |
| Prediction freshness     | max age of newest prediction         | < 60 s, 99% of the time | —              |
| Ingestion durability     | % accepted readings persisted        | 99.99%                  | —              |
| Realtime delivery        | % subscribed updates delivered < 2 s | 99%                     | —              |

## Error-budget policy

- Budget **healthy** → ship freely; canaries auto-promote.
- Budget **half spent** → slow down risky changes; require a second reviewer.
- Budget **exhausted** → feature freeze on the affected service until it
  recovers; postmortem required.

## Burn-rate alerting

Multi-window, multi-burn-rate (Google SRE workbook):

- **Fast burn** — 14.4× over a 1h/5m window pair → page (budget gone in ~2
  days at that rate).
- **Slow burn** — 3× over a 6h/1h window pair → ticket (a persistent leak).

Rules: `infra/prometheus/slo_alerts.yml`. They reference the same
`http_server_requests_seconds_*` metrics the Grafana dashboards use.
