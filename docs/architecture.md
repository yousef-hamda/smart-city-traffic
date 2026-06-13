# Architecture

> Living document — sections are filled in as the corresponding phase lands.
> The phase plan is tracked in the repository history; every service links
> back here from its own README.

## System overview

The platform is an event-driven microservices system. Simulated field devices
(traffic sensors, cameras) feed an ingestion layer; Kafka is the backbone that
decouples producers from the stream-processing, ML, and application layers.

```
sensors/cameras (simulated)
        │  MQTT / HTTP / frames
        ▼
ingestion (Spring Boot) ── vision (YOLOv8) ─────┐
        │ traffic.raw            │ vision.events │
        ▼                        ▼               ▼
   ┌─────────────────────── Kafka ────────────────────────┐
   │ traffic.raw · traffic.aggregates · traffic.events ·  │
   │ vision.frames · vision.events · predictions ·        │
   │ signal.recommendations · alerts                      │
   └──┬───────────────┬────────────────┬─────────────────┬┘
      ▼               ▼                ▼                 ▼
 Flink jobs      ML platform      RL optimizer     realtime gateway
 (windows, CEP)  (LSTM/XGB/IF,    (SUMO + SB3)     (Socket.IO fan-out)
      │           Feast, MLflow,       │                 │
      ▼           SHAP)                ▼                 ▼
 lakehouse           │           signal.recs        web / mobile
 (Iceberg/Trino/dbt) └────────────► predictions ──► dashboards
```

Stores: TimescaleDB + PostGIS (hot time-series + geospatial), Redis (online
features, rate limits, pub/sub), MongoDB (cold archives, audit logs), Neo4j
(road-network graph), MinIO + Iceberg (lake).

## Service catalog

| Service               | Stack                      | Port(s)               | Talks to                      |
| --------------------- | -------------------------- | --------------------- | ----------------------------- |
| sensor-ingestion      | Java 21 · Spring Boot 3    | 8081 http · 9091 gRPC | Postgres, Kafka, MQTT         |
| vision-service        | Python · FastAPI · YOLOv8  | 8082                  | Kafka, Redis                  |
| ml-prediction         | Python · FastAPI · gRPC    | 8083 http · 9093 gRPC | Postgres, Redis, MLflow       |
| rl-optimizer          | Python · SUMO · SB3        | 8084                  | Kafka, MLflow                 |
| federated-coordinator | Python · Flower            | 8085                  | —                             |
| ai-assistant          | Python · FastAPI · Claude  | 8086                  | Postgres, Neo4j, ChromaDB     |
| voice-gateway         | Python · FastAPI · Whisper | 8087                  | ai-assistant                  |
| api-gateway           | NestJS                     | 8080                  | Postgres, Redis, subgraphs    |
| realtime-gateway      | Node · Socket.IO           | 8088                  | Kafka, Redis                  |
| frontend              | Next.js 14                 | 3000                  | api-gateway, realtime-gateway |
| developer-portal      | Next.js 14                 | 3001                  | api-gateway                   |
| mobile                | React Native · Expo        | —                     | api-gateway                   |
| sensor-simulator      | Python CLI                 | —                     | MQTT, ingestion HTTP          |
| camera-simulator      | Python CLI                 | —                     | Kafka, RTSP                   |

## Communication paradigms — and why each is where it is

- **Kafka** — every fact that more than one consumer cares about. Topics are
  the system's public event API (see `scripts/kafka/create-topics.sh`).
- **REST** — public-facing CRUD and queries via the API gateway; simple,
  cacheable, documented with OpenAPI.
- **gRPC** — high-throughput internal calls (bulk ingestion, prediction
  serving) where schema rigor and streaming matter. Contracts in
  `packages/proto`.
- **GraphQL Federation** — the dashboard's read layer composes data owned by
  several services without the gateway hand-writing aggregation endpoints.
- **Redis pub/sub + Socket.IO** — last-mile fan-out to browsers/mobile.
- **MQTT** — device-to-cloud edge protocol from the sensor simulator,
  mirroring real ITS deployments.

## Cross-cutting

- **Observability:** OpenTelemetry SDK in every service; OTLP → Tempo
  (traces), Prometheus (metrics), Loki (logs); Grafana dashboards in
  `infra/grafana/dashboards`. Trace context propagates Java → Kafka →
  Python → gRPC → Node → browser.
- **Security:** JWT access/refresh + RBAC at the gateway; per-API-key token
  buckets in Redis; Vault (dev mode) for service credentials; Trivy in CI.
- **Multi-tenancy hook:** every domain table is keyed so a `tenant_id`
  (= city) column can be introduced additively — see ADR (planned) and
  `docs/` data-model notes.

## Decision log

Architecture Decision Records live in [`docs/adr/`](adr/):

- [0001 — Monorepo over polyrepo](adr/0001-monorepo-vs-polyrepo.md)
- [0002 — Kafka as the event backbone](adr/0002-kafka-as-backbone.md)
- [0003 — gRPC vs REST boundaries](adr/0003-grpc-vs-rest.md)
- [0004 — Iceberg for the lake](adr/0004-iceberg-for-lake.md)
- [0005 — RL for signal control](adr/0005-rl-for-signal-control.md)
- [0006 — Single schema owner](adr/0006-single-schema-owner.md)
