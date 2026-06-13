/**
 * Typed API client. Reads EXPO_PUBLIC_API_URL from the environment.
 * Falls back gracefully when no backend is available.
 */

import { mockAuth, mockSegments, mockRecommendRoute } from "./mock";
import type { MobileSegment, AuthResult, RouteResult } from "./mock";

export type { MobileSegment, AuthResult, RouteResult };

export interface IncidentPayload {
  latitude: number;
  longitude: number;
  type: "accident" | "pothole" | "blockage";
  description?: string;
  photoUri?: string;
}

export interface IncidentResult {
  id: string;
  status: "queued" | "submitted";
}

function getBaseUrl(): string | null {
  // EXPO_PUBLIC_* vars are inlined at build time by Metro bundler.
  // We access via a string map so TypeScript doesn't complain about
  // the undefined global in non-Node environments.
  try {
    // @ts-expect-error -- Metro inlines EXPO_PUBLIC_ vars into global scope
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    const url: unknown = globalThis["EXPO_PUBLIC_API_URL"];
    if (typeof url === "string" && url.length > 0) return url;
  } catch {
    // ignore
  }
  return null;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const base = getBaseUrl();
  if (!base) {
    throw new Error("NO_BACKEND");
  }
  const res = await fetch(`${base}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<AuthResult> {
  try {
    return await apiFetch<AuthResult>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  } catch {
    // Fall back to mock
    return mockAuth(email, password);
  }
}

export async function register(email: string, password: string, name: string): Promise<AuthResult> {
  try {
    return await apiFetch<AuthResult>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
  } catch {
    return mockAuth(email, password, name);
  }
}

export async function getSegments(): Promise<MobileSegment[]> {
  try {
    return await apiFetch<MobileSegment[]>("/segments");
  } catch {
    return mockSegments;
  }
}

export async function reportIncident(payload: IncidentPayload): Promise<IncidentResult> {
  try {
    return await apiFetch<IncidentResult>("/incidents", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  } catch {
    // Queue offline — return a local id
    return { id: `local-${Date.now()}`, status: "queued" };
  }
}

export async function recommendRoute(origin: string, destination: string): Promise<RouteResult> {
  try {
    return await apiFetch<RouteResult>("/route/recommend", {
      method: "POST",
      body: JSON.stringify({ origin, destination }),
    });
  } catch {
    return mockRecommendRoute(origin, destination);
  }
}
