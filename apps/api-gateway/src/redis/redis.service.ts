import { Injectable, Logger, OnModuleDestroy, OnModuleInit } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import Redis from "ioredis";
import type { AppConfig } from "../config/configuration";
import type { IRedisClient } from "./redis.interface";

@Injectable()
export class RedisService implements IRedisClient, OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(RedisService.name);
  private client!: Redis;

  constructor(private readonly config: ConfigService<AppConfig>) {}

  onModuleInit(): void {
    const url = this.config.get<string>("REDIS_URL") ?? "redis://localhost:6379";
    this.client = new Redis(url, { lazyConnect: false, enableReadyCheck: false });
    this.client.on("error", (err: Error) => {
      this.logger.warn(`Redis error (non-fatal in dev): ${err.message}`);
    });
  }

  async onModuleDestroy(): Promise<void> {
    await this.client.quit();
  }

  async get(key: string): Promise<string | null> {
    return this.client.get(key);
  }

  async set(key: string, value: string, expirySeconds?: number): Promise<void> {
    if (expirySeconds !== undefined) {
      await this.client.set(key, value, "EX", expirySeconds);
    } else {
      await this.client.set(key, value);
    }
  }

  async incr(key: string): Promise<number> {
    return this.client.incr(key);
  }

  async expire(key: string, seconds: number): Promise<void> {
    await this.client.expire(key, seconds);
  }

  async del(key: string): Promise<void> {
    await this.client.del(key);
  }
}
