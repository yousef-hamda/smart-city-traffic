/** Environment-driven configuration for the realtime gateway. */
export interface GatewayConfig {
  port: number;
  kafkaBrokers: string[];
  kafkaTopics: string[];
  consumerGroup: string;
  redisUrl: string | undefined;
  jwtAccessSecret: string;
  corsOrigin: string;
  /** Interval (ms) between global-stats broadcasts. */
  globalStatsIntervalMs: number;
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): GatewayConfig {
  return {
    port: Number(env.PORT ?? 8088),
    kafkaBrokers: (env.KAFKA_BOOTSTRAP_SERVERS ?? "localhost:29092").split(","),
    // Topics the dashboard cares about; aggregates carry the 5-min windows.
    kafkaTopics: ["traffic.aggregates", "traffic.events", "vision.events", "predictions", "alerts"],
    consumerGroup: env.KAFKA_CONSUMER_GROUP ?? "realtime-gateway",
    redisUrl: env.REDIS_URL,
    jwtAccessSecret: env.JWT_ACCESS_SECRET ?? "dev_access_secret_change_me",
    corsOrigin: env.CORS_ORIGIN ?? "*",
    globalStatsIntervalMs: Number(env.GLOBAL_STATS_INTERVAL_MS ?? 5000),
  };
}
