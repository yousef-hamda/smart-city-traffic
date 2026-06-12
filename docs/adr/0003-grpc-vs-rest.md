# ADR 0003 — gRPC for internal hot paths, REST for the public edge

Date: 2026-06-12
Status: Accepted

## Context

Services talk to each other and to the outside world with very different
requirements. Browser and third-party clients need a discoverable,
cacheable, firewall-friendly API. Internal service-to-service calls on hot
paths (bulk ingestion, model serving for the RL loop) need low latency, a
strict schema, streaming, and code-generated clients in three languages
(Java, Python, TypeScript).

Using one protocol everywhere forces a compromise: REST everywhere gives up
streaming and schema rigor on the hot paths; gRPC everywhere pushes a
binary, HTTP/2-only, browser-hostile protocol onto public clients and the
dashboard.

## Decision

Use the right protocol per boundary, and make that boundary explicit:

- **REST (+ OpenAPI)** at the public edge — everything behind the API
  gateway, plus each service's `/health`. Human-debuggable, cacheable,
  documented, easy to consume from browsers and curl.
- **gRPC** for internal hot paths with a stable contract:
  `IngestionService` (unary + client-streaming bulk) on sensor-ingestion,
  `PredictionService` on ml-prediction. Contracts live once in
  `packages/proto` and stubs are generated inside each consuming build
  (Maven `protobuf-maven-plugin` for Java, `grpcio-tools` for Python), so the
  `.proto` files are the single source of truth across languages.
- **GraphQL Federation** is layered on top for the dashboard's read model
  (ADR-adjacent, lands with the gateway) where the client wants to compose
  data owned by several services in one round trip.
- **Kafka** for fan-out events (see ADR 0002), not request/response.

## Consequences

- **Positive:** hot paths get HTTP/2 multiplexing, streaming, and
  generated, type-safe clients; a breaking field change fails the build, not
  production.
- **Positive:** public consumers keep a friendly REST/OpenAPI surface and
  never see protobuf.
- **Negative:** two serialization stacks and a codegen step to maintain; we
  contain it by generating stubs at build time (never committing generated
  code) and versioning the contract under `traffic/v1`.
- **Negative:** gRPC needs HTTP/2 end to end; the service mesh (Istio, later
  phase) handles this internally and nothing gRPC is exposed publicly.
- **Rule:** a new cross-service call picks REST unless it is a measured hot
  path or needs streaming, in which case it picks gRPC; nothing internal that
  is request/response goes over Kafka.
