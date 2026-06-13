# Realtime Gateway

WebSocket fan-out for the dashboard and mobile app. Consumes the platform's
Kafka topics and pushes live updates to subscribed browser clients over
JWT-authenticated Socket.IO, with an optional Redis adapter for horizontal
scaling.

## Flow

```
Kafka (traffic.aggregates · traffic.events · vision.events · predictions · alerts)
        │  TrafficConsumer
        ▼
  RealtimeGateway.dispatch()  ──route──►  io.to(room).emit(event, payload)
        ▲                                          │
   subscribe / unsubscribe                         ▼
   (JWT-authed Socket.IO)                    browser / mobile
```

## Channels (rooms)

| Room                | Joined via                                 | Events                                                                    |
| ------------------- | ------------------------------------------ | ------------------------------------------------------------------------- |
| `road-segment:<id>` | `subscribe { segments: [...] }`            | `segment:update`, `segment:vision`, `segment:prediction`, `segment:alert` |
| `alerts`            | `subscribe { channels: ['alerts'] }`       | `alert`                                                                   |
| `global-stats`      | `subscribe { channels: ['global-stats'] }` | `global-stats` (volatile, every 5s)                                       |

## Auth

Clients pass the API gateway's **access token** in the Socket.IO handshake
(`auth.token`); the gateway verifies it with the shared `JWT_ACCESS_SECRET`,
so identity is shared without a per-connection network call. Unauthorized
sockets are rejected at handshake (`connect_error`).

## Reliability

- **Heartbeat** — Socket.IO ping every 25s, drop after 20s silence.
- **Backpressure** — `global-stats` are emitted _volatile_ (dropped for slow
  clients instead of buffered); segment subscriptions are capped per socket.
- **Kafka resilience** — a broker outage at boot is logged and retried; the
  gateway keeps serving sockets (no live data until the broker returns).
- **Scale-out** — with `REDIS_URL` set, the `@socket.io/redis-adapter`
  publishes room emissions over Redis pub/sub so any replica can reach any
  client.

## Environment

| Variable                   | Default                 | Purpose                            |
| -------------------------- | ----------------------- | ---------------------------------- |
| `PORT`                     | `8088`                  | HTTP/WebSocket port                |
| `KAFKA_BOOTSTRAP_SERVERS`  | `localhost:29092`       | topics to fan out                  |
| `KAFKA_CONSUMER_GROUP`     | `realtime-gateway`      | consumer group                     |
| `REDIS_URL`                | _unset_                 | Socket.IO Redis adapter (optional) |
| `JWT_ACCESS_SECRET`        | —                       | must match the API gateway         |
| `CORS_ORIGIN`              | `http://localhost:3000` | allowed browser origin             |
| `GLOBAL_STATS_INTERVAL_MS` | `5000`                  | global-stats cadence               |

## Development

```bash
pnpm --filter @smart-city/realtime-gateway dev
pnpm --filter @smart-city/realtime-gateway test       # routing, auth, integration
pnpm --filter @smart-city/realtime-gateway typecheck
```
