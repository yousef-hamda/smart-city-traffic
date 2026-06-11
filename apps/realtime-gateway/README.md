# @smart-city/realtime-gateway

WebSocket fan-out gateway for the Smart City Traffic Optimization Platform,
built on plain Node + Express + Socket.IO.

Phase 1 ships a skeleton: a `/health` endpoint, a Socket.IO server that
accepts connections and immediately disconnects them, and conditional
OpenTelemetry tracing. Subscription channels (road segments, incidents,
predictions, alerts) backed by Kafka and a Redis Socket.IO adapter land in
**Phase 10**.

## Endpoints

| Method | Path      | Description                                                              |
| ------ | --------- | ------------------------------------------------------------------------ |
| GET    | `/health` | `{ "status": "ok", "service": "realtime-gateway", "version": "0.1.0" }` |
| WS     | `/socket.io` | Accepts handshake, then disconnects (channels in Phase 10)            |

## Environment variables

| Variable                      | Default | Description                                     |
| ----------------------------- | ------- | ----------------------------------------------- |
| `PORT`                        | `8088`  | HTTP/WebSocket listen port                      |
| `KAFKA_BOOTSTRAP_SERVERS`     | —       | Kafka brokers (Phase 10)                        |
| `REDIS_URL`                   | —       | Redis for the Socket.IO adapter (Phase 10)      |
| `JWT_ACCESS_SECRET`           | —       | Handshake auth secret (Phase 10)                |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | unset   | OTLP gRPC endpoint; tracing disabled when unset |

Copy `.env.example` to `.env` for local development.

## Development

```bash
pnpm --filter @smart-city/realtime-gateway dev        # ts-node-dev watch mode
pnpm --filter @smart-city/realtime-gateway build      # tsc -> dist/
pnpm --filter @smart-city/realtime-gateway test       # jest + supertest
pnpm --filter @smart-city/realtime-gateway lint
pnpm --filter @smart-city/realtime-gateway typecheck
```

The Express app is exported from `src/app.ts` separately from the listening
server (`src/server.ts`) so tests can hit `/health` without binding a port.
