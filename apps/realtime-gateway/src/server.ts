// OpenTelemetry must be imported (and started) before anything else.
import "./telemetry";

import { createServer } from "node:http";

import pino from "pino";
import { Server as SocketIOServer } from "socket.io";

import { createApp, SERVICE_NAME } from "./app";
import { loadConfig } from "./config";
import { RealtimeGateway } from "./gateway";
import { TrafficConsumer } from "./kafka";
import { attachRedisAdapter, type RedisAdapterHandle } from "./redis";

const logger = pino({ name: SERVICE_NAME });
const config = loadConfig();

const app = createApp();
const httpServer = createServer(app);

const io = new SocketIOServer(httpServer, {
  cors: { origin: config.corsOrigin },
  // Heartbeat: clients are pinged every 25s and dropped after 20s of silence.
  pingInterval: 25_000,
  pingTimeout: 20_000,
});

let redisHandle: RedisAdapterHandle | undefined;
if (config.redisUrl) {
  redisHandle = attachRedisAdapter(io, config.redisUrl, logger);
}

const gateway = new RealtimeGateway(io, config.jwtAccessSecret);
gateway.attach();
gateway.startGlobalStats(config.globalStatsIntervalMs);

const consumer = new TrafficConsumer({
  brokers: config.kafkaBrokers,
  topics: config.kafkaTopics,
  groupId: config.consumerGroup,
  gateway,
  logger,
});
void consumer.start();

httpServer.listen(config.port, () => {
  logger.info({ port: config.port }, "realtime-gateway listening");
});

const shutdown = (): void => {
  logger.info("shutting down realtime-gateway");
  gateway.stopGlobalStats();
  void consumer.stop();
  void redisHandle?.close();
  io.close();
  httpServer.close(() => process.exit(0));
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
