import { createServer, type Server as HttpServer } from "node:http";
import type { AddressInfo } from "node:net";

import jwt from "jsonwebtoken";
import { io as ioClient, type Socket as ClientSocket } from "socket.io-client";
import { Server as SocketIOServer } from "socket.io";

import { RealtimeGateway } from "../src/gateway";

const SECRET = "integration-secret";

function token(role = "analyst"): string {
  return jwt.sign({ sub: "user-1", role }, SECRET);
}

describe("RealtimeGateway (integration)", () => {
  let httpServer: HttpServer;
  let io: SocketIOServer;
  let gateway: RealtimeGateway;
  let url: string;
  const clients: ClientSocket[] = [];

  beforeAll((done) => {
    httpServer = createServer();
    io = new SocketIOServer(httpServer);
    gateway = new RealtimeGateway(io, SECRET);
    gateway.attach();
    httpServer.listen(0, () => {
      const { port } = httpServer.address() as AddressInfo;
      url = `http://localhost:${port}`;
      done();
    });
  });

  afterAll(() => {
    gateway.stopGlobalStats();
    for (const c of clients) c.close();
    io.close();
    httpServer.close();
  });

  function connect(authToken?: string): ClientSocket {
    const socket = ioClient(url, {
      auth: authToken ? { token: authToken } : {},
      transports: ["websocket"],
      reconnection: false,
    });
    clients.push(socket);
    return socket;
  }

  it("rejects a connection without a token", (done) => {
    const socket = connect();
    socket.on("connect_error", (err) => {
      expect(err.message).toMatch(/token/);
      done();
    });
  });

  it("rejects a token signed with the wrong secret", (done) => {
    const bad = jwt.sign({ sub: "u", role: "viewer" }, "wrong");
    const socket = connect(bad);
    socket.on("connect_error", (err) => {
      expect(err.message).toBeTruthy();
      done();
    });
  });

  it("delivers a segment update to a subscribed client", (done) => {
    const socket = connect(token());
    socket.on("connect", () => {
      socket.emit("subscribe", { segments: ["seg-1"] });
    });
    socket.on("subscribed", () => {
      gateway.dispatch(
        "traffic.aggregates",
        JSON.stringify({ segment_id: "seg-1", avg_speed_kmh: 25 }),
      );
    });
    socket.on("segment:update", (payload: { segment_id: string; avg_speed_kmh: number }) => {
      expect(payload.segment_id).toBe("seg-1");
      expect(payload.avg_speed_kmh).toBe(25);
      done();
    });
  });

  it("does not deliver updates for unsubscribed segments", (done) => {
    const socket = connect(token());
    socket.on("connect", () => {
      socket.emit("subscribe", { segments: ["seg-A"] });
    });
    socket.on("subscribed", () => {
      gateway.dispatch(
        "traffic.aggregates",
        JSON.stringify({ segment_id: "seg-B", avg_speed_kmh: 10 }),
      );
      // Give the server a tick; if nothing arrives, we pass.
      setTimeout(done, 150);
    });
    socket.on("segment:update", () => {
      done(new Error("received update for an unsubscribed segment"));
    });
  });

  it("broadcasts global stats to subscribers", (done) => {
    const socket = connect(token());
    socket.on("connect", () => {
      socket.emit("subscribe", { channels: ["global-stats"] });
    });
    socket.on("subscribed", () => {
      gateway.dispatch(
        "traffic.aggregates",
        JSON.stringify({ segment_id: "s", avg_speed_kmh: 40 }),
      );
      gateway.startGlobalStats(40);
    });
    socket.on("global-stats", (stats: { segments: number; avgSpeedKmh: number }) => {
      expect(stats.segments).toBeGreaterThanOrEqual(1);
      gateway.stopGlobalStats();
      done();
    });
  });
});
