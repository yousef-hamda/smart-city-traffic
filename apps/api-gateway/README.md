# @smart-city/api-gateway

Single public entry point for the Smart City Traffic Optimization Platform.

Phase 1 ships a NestJS 10 skeleton: a `/health` endpoint and conditional
OpenTelemetry tracing. REST + GraphQL Federation, authentication (JWT),
RBAC and API-key management land in **Phase 9**.

## Endpoints

| Method | Path      | Description                                          |
| ------ | --------- | ---------------------------------------------------- |
| GET    | `/health` | `{ "status": "ok", "service": "api-gateway", "version": "0.1.0" }` |

## Environment variables

| Variable                       | Default | Description                                       |
| ------------------------------ | ------- | ------------------------------------------------- |
| `PORT`                         | `8080`  | HTTP listen port                                  |
| `DATABASE_URL`                 | —       | PostgreSQL/TimescaleDB connection string (Phase 2+) |
| `REDIS_URL`                    | —       | Redis connection string (Phase 9)                 |
| `JWT_ACCESS_SECRET`            | —       | Access-token signing secret (Phase 9)             |
| `JWT_REFRESH_SECRET`           | —       | Refresh-token signing secret (Phase 9)            |
| `OTEL_EXPORTER_OTLP_ENDPOINT`  | unset   | OTLP gRPC endpoint; tracing disabled when unset   |

Copy `.env.example` to `.env` for local development.

## Development

```bash
pnpm --filter @smart-city/api-gateway dev        # watch mode
pnpm --filter @smart-city/api-gateway build      # nest build -> dist/
pnpm --filter @smart-city/api-gateway test       # jest (unit + e2e specs)
pnpm --filter @smart-city/api-gateway lint
pnpm --filter @smart-city/api-gateway typecheck
```
