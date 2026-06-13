# Smart City Traffic Optimization Platform

> Real-time traffic intelligence for a simulated Jerusalem road network —
> sensor + camera ingestion, ML congestion forecasting, RL-optimized traffic
> signals, a 3D digital twin, and a Claude-powered assistant. Built as a
> production-grade, polyglot microservices system.

**Status: under active construction.** This README tracks reality, not
aspiration — sections appear as the phases that implement them land. The full
build plan lives in the commit history (one conventional-commit series per
phase) and [`docs/architecture.md`](docs/architecture.md).

![Product tour (UI mockups)](docs/images/product-tour.gif)

> ⚠️ **The images above and below are UI previews (mockups)** — polished
> designs of the interface, **not** screenshots captured from the running app.
> They illustrate the intended product while the frontend is wired up. The
> traffic data throughout the platform comes from clearly-labeled simulators.

## New here? Start with the fun tour 🎉

Not a developer? Open [**`EXPLAINER.html`**](EXPLAINER.html) in any web browser
(or read [**`EXPLAINER.pdf`**](EXPLAINER.pdf)) for an animated, plain-language
tour of what this project does and how it works — no technical knowledge needed.

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

| Surface               | URL                        |
| --------------------- | -------------------------- |
| Dashboard             | http://localhost:3000      |
| API gateway (Swagger) | http://localhost:8080/docs |
| Developer portal      | http://localhost:3001      |

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

## Screenshots

> **UI previews (mockups)** — interface designs, not captures of the running app.

|                                                             |                                                                             |
| ----------------------------------------------------------- | --------------------------------------------------------------------------- |
| ![Dashboard (mockup)](docs/images/mockup_01_dashboard.png)  | ![Segment drill-down with SHAP (mockup)](docs/images/mockup_02_segment.png) |
| **Live dashboard** — map, KPIs, alerts                      | **Segment drill-down** — forecast + SHAP                                    |
| ![3D digital twin (mockup)](docs/images/mockup_03_twin.png) | ![AI assistant (mockup)](docs/images/mockup_04_assistant.png)               |
| **3D digital twin**                                         | **AI assistant** (EN · עברית · العربية)                                     |

## Documentation

- [Architecture](docs/architecture.md) · [ADRs](docs/adr/)
- Plain-language tour: [EXPLAINER.html](EXPLAINER.html) · [EXPLAINER.pdf](EXPLAINER.pdf)
- Per-service READMEs under `apps/<service>/README.md`

## License

[MIT](LICENSE) — © Yousef Hasan Hamda
([LinkedIn](https://www.linkedin.com/in/yousef-hamda-1093a4352) ·
yousef123hamda@gmail.com)
