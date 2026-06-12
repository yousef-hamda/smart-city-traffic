# ADR 0002 — Kafka as the event backbone

Date: 2026-06-12
Status: Accepted

## Context

Sensor readings and vision events are produced continuously and consumed by
many independent subsystems: stream processing (Flink), the ML platform, the
RL optimizer, the realtime gateway, and the data lake. These consumers have
different throughput, latency, and availability characteristics, and the set
of consumers grows over time (a new analytics job, a new model trainer).

We need an integration style that:

- decouples producers from consumers in both time and space — a slow or
  down consumer must not back-pressure ingestion;
- lets new consumers join and replay history without touching producers;
- preserves per-entity ordering (all readings for a segment in order);
- survives consumer restarts without losing data.

Alternatives considered: direct service-to-service REST/gRPC fan-out (couples
producers to every consumer, no replay, no buffering); a database-as-queue
(poll amplification, no native fan-out); RabbitMQ/SQS (great for task queues,
weaker for high-throughput replayable event logs and per-key ordering).

## Decision

Apache Kafka (KRaft mode — no ZooKeeper) is the platform's event backbone.
Topics are the public, versioned event API between services; producers write,
any number of consumer groups read independently. Keys carry the partitioning
identity (segment id) so per-segment ordering holds while partitions give
horizontal scale. Topic list and retention live in
`scripts/kafka/create-topics.sh`.

The ingestion service still writes readings to TimescaleDB synchronously
(durability for the system of record) _and_ publishes to `traffic.raw`; the
Kafka publish is wrapped in a Resilience4j circuit breaker so a Kafka outage
degrades to "persisted but not yet streamed" rather than dropping the request.

## Consequences

- **Positive:** consumers are added/removed with zero producer changes;
  replay (new model, backfill) is a consumer-offset reset; natural buffering
  absorbs bursts and slow consumers.
- **Positive:** one mental model (the log) spans Java, Python, and Node
  services; trace context propagates through Kafka headers for end-to-end
  tracing.
- **Negative:** operational surface (a broker to run, monitor, and size);
  mitigated in dev by a single-broker KRaft container with healthchecks.
- **Negative:** at-least-once delivery means consumers must be idempotent;
  we key writes by natural ids and use upserts where it matters.
- **Trade-off accepted:** ordering is per-partition, not global. The data
  model never requires cross-segment global ordering, so this is free.
