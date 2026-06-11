# ADR 0001 — Monorepo over polyrepo

Date: 2026-06-11
Status: Accepted

## Context

The platform spans fourteen deployable services in four language ecosystems
(TypeScript, Python, Java, plus infra-as-code), shared gRPC contracts, shared
TypeScript types, and shared translation catalogs. We need to choose between
one repository for everything or one repository per service.

Forces at play:

- Cross-service changes (a new field on `SensorReading` touches the proto
  contract, the Java producer, the Python consumers, and the TS dashboard)
  should be reviewable and revertable as one unit.
- The project is also a portfolio artifact: a reviewer should be able to clone
  one URL, run `make dev`, and explore the entire system.
- A single maintainer operates this. Polyrepo coordination overhead
  (versioning shared packages, cross-repo CI triggers, release trains) has no
  payoff at this team size.
- Services must remain *independently deployable* regardless of repo layout.

## Decision

A single monorepo, organized as `apps/*` (deployables), `packages/*` (shared
contracts/types/UI/i18n), with pnpm workspaces for the TS estate and
self-contained `pyproject.toml`/`pom.xml` builds per non-TS service.
Independent deployability is preserved at the artifact level: every service
has its own Dockerfile, image, Helm subchart, and CI matrix entry — nothing
at runtime depends on a sibling's source tree.

## Consequences

- **Positive:** atomic cross-service commits; one CI pipeline with per-language
  jobs; a single `docker-compose.yml` describing the whole system; shared
  `.proto` files are the single source of truth for gRPC contracts.
- **Positive:** drastically lower onboarding cost for reviewers.
- **Negative:** CI must be path-aware as the repo grows or build times suffer;
  we accept matrix-per-service jobs now and can adopt Nx/Turborepo task
  graphs later without restructuring.
- **Negative:** git history interleaves all services; we mitigate with
  conventional-commit scopes (`feat(vision-service): …`).
- **Risk accepted:** a monorepo can tempt accidental source-level coupling
  between services; the rule is that cross-service interaction happens only
  via published interfaces (Kafka topics, REST/gRPC/GraphQL, `packages/*`).
