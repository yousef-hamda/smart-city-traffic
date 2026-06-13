# Chaos Game-Day Playbook

We don't trust resilience we haven't tested. A game-day runs the
`infra/litmus/` experiments against a staging cluster while we watch Grafana
and confirm the system degrades the way we designed it to.

## Before you start

- Staging cluster with the platform deployed (`make k8s-up`), Litmus installed,
  and the `litmus-admin` service account present.
- Grafana open on **Platform Overview** + **Traffic KPIs**; Alertmanager
  reachable. A simulator running (`make sim`) so there's live traffic.
- Announce the window; this is staging, never production.

## Experiments

Run with `make chaos` (`kubectl apply -f infra/litmus/`) one at a time.

### 1. Pod delete — ml-prediction (`pod-delete-prediction-service.yaml`)

- **Hypothesis:** killing pods causes a brief blip; predictions keep flowing
  via the remaining replicas + Istio retries; no sustained budget burn.
- **Watch:** the experiment's `httpProbe` stays green; p95 latency spikes then
  recovers; `ServiceDown` does **not** fire (replicas > 1).
- **Bad outcome:** predictions stop, `PredictionStaleness` fires and stays →
  replica count or PDB is wrong.

### 2. Network loss — Kafka (`network-loss-kafka.yaml`)

- **Hypothesis:** producers can't reach Kafka; the ingestion **circuit breaker
  opens**; readings are still persisted to Postgres (degraded to
  "persisted, not streamed"), not dropped.
- **Watch:** `KafkaConsumerLagGrowing` may fire; ingestion `readings_ingested_total`
  keeps climbing while `traffic.raw` publish errors are logged; on recovery the
  breaker closes and the stream catches up.
- **Bad outcome:** ingestion 5xx-es and drops readings → the breaker fallback
  is mis-wired.

### 3. CPU stress — realtime gateway (`cpu-stress-realtime-gateway.yaml`)

- **Hypothesis:** backpressure drops volatile `global-stats`; heartbeats keep
  healthy sockets; the HPA scales out.
- **Watch:** segment updates still arrive for subscribed clients; CPU panel
  saturates then new replicas appear.
- **Bad outcome:** sockets mass-disconnect → heartbeat/backpressure tuning is
  off.

### 4. Disk fill — Postgres (`disk-fill-postgres.yaml`)

- **Hypothesis:** disk-pressure alerts fire; writes fail **gracefully**; we
  follow the disk-pressure procedure.
- **Watch:** alerts in Alertmanager; ingestion returns clean 5xx (not crash
  loops); after cleanup, writes resume.
- **Bad outcome:** Postgres corrupts or the service crash-loops.

## After

For each experiment, record: did reality match the hypothesis? Any alert that
should have fired but didn't (or fired late)? File follow-ups. A game-day with
zero findings usually means the experiments were too gentle — make the next one
harder.
