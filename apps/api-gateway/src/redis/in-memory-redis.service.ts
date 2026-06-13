import type { IRedisClient } from "./redis.interface";

export class InMemoryRedisService implements IRedisClient {
  private readonly store = new Map<string, { value: string; expiresAt?: number }>();

  async get(key: string): Promise<string | null> {
    const entry = this.store.get(key);
    if (!entry) return null;
    if (entry.expiresAt !== undefined && Date.now() > entry.expiresAt) {
      this.store.delete(key);
      return null;
    }
    return entry.value;
  }

  async set(key: string, value: string, expirySeconds?: number): Promise<void> {
    const expiresAt = expirySeconds !== undefined ? Date.now() + expirySeconds * 1000 : undefined;
    this.store.set(key, { value, expiresAt });
  }

  async incr(key: string): Promise<number> {
    const current = await this.get(key);
    const next = current !== null ? parseInt(current, 10) + 1 : 1;
    const entry = this.store.get(key);
    this.store.set(key, { value: String(next), expiresAt: entry?.expiresAt });
    return next;
  }

  async expire(key: string, seconds: number): Promise<void> {
    const entry = this.store.get(key);
    if (entry) {
      this.store.set(key, { ...entry, expiresAt: Date.now() + seconds * 1000 });
    }
  }

  async del(key: string): Promise<void> {
    this.store.delete(key);
  }
}
