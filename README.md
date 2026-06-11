# Smart City Traffic Optimization Platform

> Real-time traffic intelligence for a simulated Jerusalem road network —
> sensor + camera ingestion, ML congestion forecasting, RL-optimized traffic
> signals, a 3D digital twin, and a Claude-powered assistant. Built as a
> production-grade, polyglot microservices system.

**Status: under active construction.** This README tracks reality, not
aspiration — sections appear as the phases that implement them land. The full
build plan lives in the commit history (one conventional-commit series per
phase) and [`docs/architecture.md`](docs/architecture.md).

## What it is

A multi-service platform that ingests live traffic telemetry (from honest,
clearly-labeled **simulators** — the engineering value is the system, not the
data source), processes it through Kafka and Flink, predicts congestion with
classical and deep-learning models, optimizes signal timing with reinforcement
learning against SUMO, and serves it all through a real-time geospatial
dashboard, a citizen mobile app, and a voice-and-text AI assistant — in
English, Hebrew (RTL), and Arabic (RTL).

## Quick start

```bash
# prerequisites: Docker Desktop, pnpm ≥ 9, GNU make
make dev        # full stack: infra + all services
make dev-infra  # just Postgres/Kafka/Redis/Mongo/Neo4j/MinIO/Mosquitto
make seed       # seed road segments, sensors, cameras, Neo4j graph
make sim        # start the sensor simulator
```

| Surface | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API gateway (Swagger) | http://localhost:8080/docs |
| Developer portal | http://localhost:3001 |

## Repository layout

```
apps/        14 deployable services (TS · Python · Java)
packages/    shared contracts: types · proto · ui · i18n
ml/          notebooks · training data · Feast repo · model artifacts
analytics/   dbt models · Superset dashboards
flink/       streaming jobs (windows + CEP)
neo4j/       road-graph seed + Cypher
infra/       docker · k8s · helm · istio · argocd · terraform · observability
docs/        architecture · ADRs · runbooks · chaos game-day
scripts/     seeds · kafka topics · load tests · security scans
```

## Documentation

- [Architecture](docs/architecture.md) · [ADRs](docs/adr/)
- Per-service READMEs under `apps/<service>/README.md`

## License

[MIT](LICENSE) — © Yousef Hasan Hamda
([LinkedIn](https://www.linkedin.com/in/yousef-hamda-1093a4352) ·
yousef123hamda@gmail.com)
