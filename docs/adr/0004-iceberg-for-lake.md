# ADR 0004 — Apache Iceberg for the data lake

Date: 2026-06-13
Status: Accepted

## Context

Operational stores (TimescaleDB, Redis, Mongo, Neo4j) serve the live product,
but analytics and ML need cheap, long-horizon, queryable history that isn't
bounded by a database's hot storage. We want a lakehouse on object storage
(MinIO/S3) that:

- holds raw and modelled tables affordably and at scale;
- supports SQL from multiple engines (Trino for BI/dbt, Flink for streaming
  writes, Spark later if needed) over the _same_ tables;
- gives correctness on a mutable lake — atomic commits, no half-written
  partitions, safe concurrent writers;
- evolves schema as upstream events change, without rewriting history;
- enables time travel for reproducible training sets and audits.

Plain Parquet-on-S3 with Hive-style directories gives none of the transactional
or schema-evolution guarantees; Delta Lake and Apache Hudi are credible
alternatives.

## Decision

Use **Apache Iceberg** tables in MinIO as the lake format, queried by **Trino**
and written by **Flink**. dbt (`dbt-trino`) builds staging and marts on top.

Iceberg is chosen over Delta/Hudi for: first-class **multi-engine** support
(Flink and Trino both write/read Iceberg natively, which this project needs —
streaming ingest _and_ interactive SQL on one table); hidden partitioning and
**partition evolution** (change the partition scheme without rewriting data);
mature **schema evolution**; and **snapshot/time-travel** semantics that make
reproducible ML datasets trivial.

## Consequences

- **Positive:** one set of governed tables serves streaming writes (Flink),
  interactive SQL/BI (Trino + Superset), and transformations (dbt) — no copies
  to keep in sync.
- **Positive:** ACID commits mean a failed Flink checkpoint never leaves a
  partially-visible partition; analysts never read torn data.
- **Positive:** time travel (`FOR VERSION AS OF`) gives reproducible training
  snapshots and cheap audits.
- **Negative:** more moving parts than Parquet-on-S3 — a catalog plus the
  Iceberg/S3 connectors on Flink's and Trino's classpaths. In dev we use a
  file-based (Hadoop) catalog to avoid running a metastore; production would
  use a REST or Glue catalog.
- **Negative:** the team must understand Iceberg's snapshot/metadata model to
  reason about compaction and expiration; documented in `docs/data-lake.md`.
- **Trade-off accepted:** Delta has deeper Spark ergonomics, but this platform
  leads with Flink + Trino, where Iceberg's multi-engine support is the
  decisive advantage.
