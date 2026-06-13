import { z } from "zod";

const configSchema = z.object({
  PORT: z.coerce.number().default(8080),
  DATABASE_URL: z.string().min(1).default("postgresql://localhost:5432/smartcity"),
  REDIS_URL: z.string().default("redis://localhost:6379"),
  JWT_ACCESS_SECRET: z.string().min(1).default("dev-access-secret-change-in-production"),
  JWT_REFRESH_SECRET: z.string().min(1).default("dev-refresh-secret-change-in-production"),
  JWT_ACCESS_TTL: z.coerce.number().default(900),
  JWT_REFRESH_TTL: z.coerce.number().default(604800),
  PREDICTION_SUBGRAPH_URL: z.string().optional(),
  ASSISTANT_SUBGRAPH_URL: z.string().optional(),
});

export type AppConfig = z.infer<typeof configSchema>;

export function validateConfig(config: Record<string, unknown>): AppConfig {
  return configSchema.parse(config);
}
