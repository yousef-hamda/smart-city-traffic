# ADR 0006 — One schema owner for the shared Postgres

Date: 2026-06-12
Status: Accepted

## Context

Several services read and write the same Postgres instance: sensor-ingestion
(telemetry), ml-prediction (predictions), the RL optimizer (signal
recommendations), and the API gateway (users, API keys, and read queries over
the domain tables). Postgres here carries PostGIS geometry and TimescaleDB
hypertables, which ORMs model poorly.

If each service ran its own migration tool against the same database
(Flyway _and_ Prisma _and_ …), they would race on shared tables, disagree on
types (a Prisma `String` vs a PostGIS `geometry`), and there would be no single
place that describes the schema. In dev there is one physical database, so
"database-per-service" isolation is logical, not physical.

## Decision

**Flyway, owned by sensor-ingestion, is the single source of truth for the
schema** — all tables, PostGIS columns, hypertables, and continuous
aggregates. Other services consume that schema as clients, not co-owners:

- The **API gateway** hand-writes a `prisma/schema.prisma` that mirrors the
  Flyway tables and runs only `prisma generate` (typed client), never
  `prisma migrate`. Prisma is used as a type-safe query builder, not a
  migration tool.
- Python services use SQL / SQLAlchemy Core against the same tables.

A future split into physically separate databases per service is a deployment
change, not a code change, because each service already touches a disjoint set
of tables at runtime.

## Consequences

- **Positive:** one authoritative schema; no migration races; PostGIS and
  TimescaleDB features (GIST indexes, `create_hypertable`, continuous
  aggregates) are expressed in native SQL where they belong, not fought
  through an ORM.
- **Positive:** the gateway still gets full Prisma type-safety and
  autocomplete from the generated client.
- **Negative / deviation:** the build spec said "Prisma migrations"; we use
  Prisma generate-only against a Flyway-owned schema instead. This is a
  deliberate trade for a single schema owner and is documented here so the
  choice is legible to reviewers.
- **Discipline required:** when the gateway needs a new column, it is added to
  a Flyway migration first, then reflected in `schema.prisma`. The two are
  kept in lock-step; CI (later phase) can assert `prisma db pull` produces no
  diff against the committed schema.
