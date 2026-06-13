export interface IRedisClient {
  get(key: string): Promise<string | null>;
  set(key: string, value: string, expirySeconds?: number): Promise<void>;
  incr(key: string): Promise<number>;
  expire(key: string, seconds: number): Promise<void>;
  del(key: string): Promise<void>;
}

export const REDIS_CLIENT = "REDIS_CLIENT";
