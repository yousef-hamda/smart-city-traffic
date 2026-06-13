/** Optional Redis adapter so multiple gateway replicas share rooms.
 *
 * With the adapter, a record consumed by replica A reaches a client connected
 * to replica B: Socket.IO publishes room emissions over Redis pub/sub. Without
 * a REDIS_URL the gateway runs single-node (fine for dev).
 */
import { createAdapter } from "@socket.io/redis-adapter";
import { Redis } from "ioredis";
import type { Logger } from "pino";
import type { Server } from "socket.io";

export interface RedisAdapterHandle {
  close: () => Promise<void>;
}

export function attachRedisAdapter(
  io: Server,
  redisUrl: string,
  logger: Logger,
): RedisAdapterHandle {
  const pubClient = new Redis(redisUrl, { lazyConnect: false });
  const subClient = pubClient.duplicate();
  io.adapter(createAdapter(pubClient, subClient));
  logger.info("socket.io redis adapter attached");
  return {
    close: async () => {
      pubClient.disconnect();
      subClient.disconnect();
    },
  };
}
