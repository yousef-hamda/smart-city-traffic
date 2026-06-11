# sensor-ingestion

Java (Spring Boot) service that ingests raw traffic-sensor telemetry for the Smart City
Traffic Optimization Platform. In its final form it consumes sensor payloads over MQTT,
enriches them with road-segment geometry from PostGIS, and publishes normalized events to
Kafka, while exposing a gRPC API for internal lookups.

**Current status: Phase 1 skeleton.** The service boots, exposes health/metrics endpoints
and is OpenTelemetry-ready. All business logic lands in Phase 2.

## Interfaces

| Interface | Protocol | Endpoint / Topic | Status |
| --- | --- | --- | --- |
| Service health | REST | `GET /health` | Available |
| Actuator health | REST | `GET /actuator/health` | Available |
| Actuator info | REST | `GET /actuator/info` | Available |
| Prometheus metrics | REST | `GET /actuator/prometheus` | Available |
| Raw sensor intake | MQTT (Paho) | `sensors/+/telemetry` | Phase 2 |
| Enriched events out | Kafka | `traffic.sensor.enriched` | Phase 2 |
| Sensor lookup API | gRPC (port 9091) | `SensorIngestionService` | Phase 2 |

## Environment variables

| Variable | Purpose | Status |
| --- | --- | --- |
| `SPRING_DATASOURCE_URL` | PostGIS JDBC URL for geo-enrichment | Phase 2 |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka brokers for enriched events | Phase 2 |
| `MQTT_BROKER_URL` | MQTT broker for raw sensor payloads | Phase 2 |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint (traces/metrics) | Available |
| `OTEL_SDK_DISABLED` | Set `false` to enable OTel export (default `true`) | Available |
| `DEPLOY_ENV` | `deployment.environment` resource attribute (default `local`) | Available |

See [.env.example](.env.example).

## Run

Requires Java 21 (Homebrew: `/opt/homebrew/opt/openjdk@21`).

```bash
cd apps/sensor-ingestion
JAVA_HOME=/opt/homebrew/opt/openjdk@21 ./mvnw spring-boot:run
```

The service listens on **8081**:

```bash
curl http://localhost:8081/health
# {"status":"ok","service":"sensor-ingestion","version":"0.1.0"}
```

## Test

```bash
JAVA_HOME=/opt/homebrew/opt/openjdk@21 ./mvnw verify
```

`verify` also runs Checkstyle (google_checks, warnings only for now). SpotBugs is
commented out in `pom.xml` and gets enabled in the Phase 21 CI hardening pass.

## Observability

- **Metrics:** Micrometer + Prometheus registry, scrape `GET /actuator/prometheus`.
- **Logs:** structured JSON (ECS format) on the console via
  `logging.structured.format.console=ecs` (takes effect on Spring Boot 3.4+; the 3.3
  parent ignores it and logs plain text). Override the property locally for
  human-readable output.
- **Traces/metrics export:** `opentelemetry-spring-boot-starter` is on the classpath but
  the SDK is disabled by default (`otel.sdk.disabled=${OTEL_SDK_DISABLED:true}`), so the
  skeleton runs without a collector. To export, set `OTEL_SDK_DISABLED=false` and
  `OTEL_EXPORTER_OTLP_ENDPOINT` (e.g. `http://otel-collector:4318`).
- **Graceful shutdown:** enabled (`server.shutdown=graceful`, 20s per phase) so in-flight
  requests drain on SIGTERM.

## Docker

Built from the **repo root** (multi-stage, non-root, healthchecked):

```bash
docker build -f infra/docker/sensor-ingestion.Dockerfile -t smart-city/sensor-ingestion .
```

Exposes 8081 (HTTP) and 9091 (gRPC, Phase 2).
