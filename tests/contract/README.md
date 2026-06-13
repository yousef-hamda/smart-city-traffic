# Contract Tests (Pact)

Consumer-driven contracts between services so a provider can't break a consumer
without CI catching it.

- `ml-prediction.pact.spec.ts` — the API gateway's expectation of
  ml-prediction's `POST /forecast/demand`. Generates a pact in `pacts/`; the
  provider verifies it in its own pipeline (and/or a Pact Broker).

```bash
pnpm --filter @smart-city/contract-tests test
```

Runs offline (Pact spins up a local mock provider).
