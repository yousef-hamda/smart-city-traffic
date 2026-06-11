# @smart-city/proto

Single source of truth for every gRPC contract in the platform. Services
never copy `.proto` files — build tooling points here.

| File                                | Service             | Server                         | Consumers                       |
| ----------------------------------- | ------------------- | ------------------------------ | ------------------------------- |
| `proto/traffic/v1/ingestion.proto`  | `IngestionService`  | sensor-ingestion (Java, :9091) | sensor-simulator, backfill jobs |
| `proto/traffic/v1/prediction.proto` | `PredictionService` | ml-prediction (Python, :9093)  | rl-optimizer, api-gateway       |

## Generation

Stubs are generated inside each consuming service's own build (Maven plugin /
`grpcio-tools` / buf) rather than committed here — see `pnpm generate` for the
per-language pointers. This keeps generated code out of review while the
contract stays versioned and diffable.

## Evolution rules

- Additive changes only within `v1` (new fields, new RPCs); field numbers are
  never reused.
- Breaking changes require a `traffic/v2` package and a documented migration.
