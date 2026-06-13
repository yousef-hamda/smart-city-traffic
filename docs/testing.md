# Testing

The test pyramid across the polyglot estate, and how each layer runs.

## Unit & integration (per service, in CI)

| Ecosystem  | Runner                 | Notes                                                                     |
| ---------- | ---------------------- | ------------------------------------------------------------------------- |
| TypeScript | Jest (+ RTL)           | gateways, frontend, mobile, packages                                      |
| Python     | pytest                 | services; `pytest-cov` with **`--cov-fail-under=70`** on covered services |
| Java       | JUnit + Testcontainers | ingestion (integration gated to skip without Docker)                      |

Coverage gate: services with a measured ≥70% enforce it in their
`pyproject.toml` (`--cov-fail-under=70`) — currently federated-coordinator
(83%), sensor-simulator (90%), camera-simulator (92%), vision-service (89%).
The gate ratchets onto more services as their suites grow.

## Contract (Pact)

`tests/contract/` holds consumer-driven contracts so a provider can't break a
consumer silently. `ml-prediction.pact.spec.ts` encodes the API gateway's
expectation of `POST /forecast/demand`; Pact stands up a local mock provider,
the consumer test runs against it, and the generated pact is verified by the
provider. Runs offline.

```bash
pnpm --filter @smart-city/contract-tests test     # or: make test-contract
```

## End-to-end (Playwright)

`apps/frontend/e2e/` — three journeys against the dev server (mock data, no
backend needed): the dashboard → segment drill-down, the assistant voice/ask
affordance, and the en→he **RTL switch**.

```bash
make test-e2e        # pnpm --filter @smart-city/frontend test:e2e
```

## Mobile (Maestro)

`.maestro/incident-report.yaml` — log in and submit an incident report on a
simulator/device.

```bash
maestro test .maestro/incident-report.yaml
```

## Load (k6)

`scripts/load/` — `ingestion.js` (~10k readings/min for 1 min, p95 < 500ms)
and `api.js` (500 RPS for 2 min, p95 < 300ms). Thresholds fail the run.

```bash
make test-load       # k6 run scripts/load/api.js
```
