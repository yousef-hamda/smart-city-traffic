// OpenTelemetry must be imported (and started) before anything else.
import './telemetry';

import { createServer } from 'node:http';

import pino from 'pino';
import { Server as SocketIOServer } from 'socket.io';

import { createApp, SERVICE_NAME } from './app';

const logger = pino({ name: SERVICE_NAME });

const app = createApp();
const httpServer = createServer(app);

const io = new SocketIOServer(httpServer, {
  cors: {
    // TODO(Phase 10): restrict to the frontend origins once channels exist.
    origin: process.env.CORS_ORIGIN ?? '*',
  },
});

io.on('connection', (socket) => {
  // Subscription channels (segments, incidents, predictions, alerts) land in
  // Phase 10. Until then we acknowledge the handshake and disconnect.
  logger.info({ socketId: socket.id }, 'socket connected — no channels yet, disconnecting');
  socket.disconnect(true);
});

const port = Number(process.env.PORT ?? 8088);
httpServer.listen(port, () => {
  logger.info({ port }, 'realtime-gateway listening');
});

const shutdown = (): void => {
  logger.info('shutting down realtime-gateway');
  io.close();
  httpServer.close(() => process.exit(0));
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
