/** Socket.IO gateway: authentication, room subscriptions, and fan-out.
 *
 * - JWT auth runs as connection middleware (one verification per socket).
 * - Clients `subscribe` to segment rooms and the alerts / global-stats
 *   channels; the gateway joins/leaves Socket.IO rooms accordingly.
 * - `dispatch()` is called by the Kafka consumer for each record and fans it
 *   out to the right rooms via the pure `routeMessage` rules.
 * - global-stats are broadcast on a timer as *volatile* emits, so a slow
 *   client drops stale stats instead of building unbounded backlog
 *   (lightweight backpressure). Socket.IO's ping/pong supplies heartbeats.
 */
import type { Server, Socket } from "socket.io";

import { AuthError, verifyAccessToken, type AccessTokenClaims } from "./auth";
import { ALERTS_ROOM, GLOBAL_STATS_ROOM, GlobalStats, routeMessage, segmentRoom } from "./routing";

/** Hard cap on segment subscriptions per socket — abuse / memory guard. */
const MAX_SEGMENT_SUBSCRIPTIONS = 200;

export interface SubscribePayload {
  segments?: string[];
  channels?: Array<typeof ALERTS_ROOM | typeof GLOBAL_STATS_ROOM>;
}

interface AuthedSocket extends Socket {
  data: { user?: AccessTokenClaims };
}

export class RealtimeGateway {
  private readonly stats = new GlobalStats();
  private statsTimer: NodeJS.Timeout | undefined;

  constructor(
    private readonly io: Server,
    private readonly jwtAccessSecret: string,
  ) {}

  /** Install auth middleware and connection handlers. Call once at startup. */
  attach(): void {
    this.io.use((socket, next) => {
      const token = socket.handshake.auth?.token as string | undefined;
      if (!token) {
        next(new Error("missing auth token"));
        return;
      }
      try {
        (socket as AuthedSocket).data.user = verifyAccessToken(token, this.jwtAccessSecret);
        next();
      } catch (err) {
        next(new Error(err instanceof AuthError ? err.message : "unauthorized"));
      }
    });

    this.io.on("connection", (socket) => this.onConnection(socket as AuthedSocket));
  }

  private onConnection(socket: AuthedSocket): void {
    socket.on("subscribe", (payload: SubscribePayload) => this.onSubscribe(socket, payload));
    socket.on("unsubscribe", (payload: SubscribePayload) => this.onUnsubscribe(socket, payload));
  }

  private onSubscribe(socket: AuthedSocket, payload: SubscribePayload): void {
    const segments = (payload.segments ?? []).filter((s) => typeof s === "string");
    for (const segmentId of segments.slice(0, MAX_SEGMENT_SUBSCRIPTIONS)) {
      void socket.join(segmentRoom(segmentId));
    }
    for (const channel of payload.channels ?? []) {
      if (channel === ALERTS_ROOM || channel === GLOBAL_STATS_ROOM) {
        void socket.join(channel);
      }
    }
    socket.emit("subscribed", {
      segments: segments.slice(0, MAX_SEGMENT_SUBSCRIPTIONS),
      channels: payload.channels ?? [],
    });
  }

  private onUnsubscribe(socket: AuthedSocket, payload: SubscribePayload): void {
    for (const segmentId of payload.segments ?? []) {
      void socket.leave(segmentRoom(segmentId));
    }
    for (const channel of payload.channels ?? []) {
      void socket.leave(channel);
    }
  }

  /** Fan one Kafka record out to subscribed rooms and update global stats. */
  dispatch(topic: string, value: string | Buffer | null): void {
    this.stats.ingest(topic, value);
    for (const { room, event, payload } of routeMessage(topic, value)) {
      this.io.to(room).emit(event, payload);
    }
  }

  /** Begin periodic global-stats broadcasts (volatile = drop-if-slow). */
  startGlobalStats(intervalMs: number): void {
    this.statsTimer = setInterval(() => {
      this.io.to(GLOBAL_STATS_ROOM).volatile.emit("global-stats", this.stats.snapshot());
    }, intervalMs);
  }

  stopGlobalStats(): void {
    if (this.statsTimer) clearInterval(this.statsTimer);
    this.statsTimer = undefined;
  }
}
