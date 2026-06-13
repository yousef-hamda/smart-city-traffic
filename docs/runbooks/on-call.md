# On-Call Runbooks

What to do when a specific alert fires. Each entry: symptom → likely cause →
checks → mitigation.

## Prediction latency spike (`HighP95Latency` on ml-prediction)

- **Likely cause:** a slow model version (bad canary), CPU starvation, or a
  cold model reload.
- **Check:** Grafana p95 panel by version; is a canary in progress? `kubectl
argo rollouts get rollout ml-prediction`. Pod CPU throttling?
- **Mitigate:** if a canary is the culprit, `kubectl argo rollouts abort
ml-prediction` (auto-rolls back to stable — the AnalysisTemplate should have
  done this already). If CPU-bound, bump replicas/limits.

## Kafka consumer lag growing (`KafkaConsumerLagGrowing`)

- **Likely cause:** a stuck or under-scaled consumer (vision-service, Flink,
  realtime-gateway), or a Kafka partition imbalance.
- **Check:** which `consumergroup` is lagging? Is the consumer pod healthy and
  committing offsets? Broker health.
- **Mitigate:** restart the stuck consumer; scale its replicas / Flink
  parallelism; verify partition count ≥ consumer count. Lag should drain.

## Predictions stale (`PredictionStaleness`)

- **Likely cause:** ml-prediction down, or its inputs (Feast/Redis, Postgres)
  unavailable, or upstream ingestion stopped.
- **Check:** `/health` on ml-prediction; is ingestion still writing
  (`readings_ingested_total` rate > 0)? Redis/Postgres up?
- **Mitigate:** restore the failed dependency; if ingestion is the root cause,
  see below. Confirm freshness recovers < 60 s.

## Ingestion dropped to zero (`readings_ingested_total` flat)

- **Likely cause:** simulators/devices stopped, MQTT broker down, or the
  ingestion service crashed.
- **Check:** ingestion `/actuator/health`; Mosquitto reachable; are simulators
  running? Look for the MQTT subscriber reconnect logs.
- **Mitigate:** restart Mosquitto / the ingestion service; restart simulators
  (`make sim`). The MQTT subscriber reconnects automatically once the broker
  returns.

## Model canary failing (Rollout degraded)

- **Likely cause:** the new model regressed p95 latency or success rate; the
  AnalysisTemplate aborted the rollout.
- **Check:** `kubectl argo rollouts get rollout ml-prediction` for the failed
  analysis run + which metric tripped.
- **Mitigate:** the rollout already reverted to stable — no traffic at risk.
  Investigate the new model offline (it's the same artifact the notebooks
  evaluate), fix, and re-deploy. Do **not** force-promote a failing canary.

## Error-budget burn (`ApiErrorBudgetFastBurn`)

- See [`slos.md`](slos.md). Fast burn = page. Find the failing dependency
  (5xx by route in Grafana → trace in Tempo → logs in Loki via trace_id) and
  apply the relevant runbook above. Enact the error-budget policy (freeze risky
  changes until recovered).
