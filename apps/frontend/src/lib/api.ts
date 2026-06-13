// REST API client — falls back to mock data when the backend is unavailable.

import {
  getMockSegments,
  getMockGlobalStats,
  getMockAlerts,
  getMockSegmentHistory,
  getMockShapContributions,
  getMockPrediction,
} from "./mock";
import type { SegmentState, GlobalStats, Alert, SegmentHistory, ShapContribution } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

let _usingMock = false;

export function isUsingMockData(): boolean {
  return _usingMock;
}

async function fetchWithFallback<T>(url: string, fallback: () => T): Promise<T> {
  if (typeof window === "undefined") {
    // SSR — always use mock to avoid network calls during build
    _usingMock = true;
    return fallback();
  }
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    _usingMock = false;
    return res.json() as Promise<T>;
  } catch {
    _usingMock = true;
    return fallback();
  }
}

export async function fetchSegments(): Promise<SegmentState[]> {
  return fetchWithFallback(`${API_BASE}/api/v1/segments`, getMockSegments);
}

export async function fetchGlobalStats(): Promise<GlobalStats> {
  return fetchWithFallback(`${API_BASE}/api/v1/stats`, getMockGlobalStats);
}

export async function fetchAlerts(): Promise<Alert[]> {
  return fetchWithFallback(`${API_BASE}/api/v1/alerts`, getMockAlerts);
}

export async function fetchSegmentHistory(segmentId: string): Promise<SegmentHistory> {
  return fetchWithFallback(`${API_BASE}/api/v1/segments/${segmentId}/history`, () =>
    getMockSegmentHistory(segmentId),
  );
}

export async function fetchShapContributions(segmentId: string): Promise<ShapContribution[]> {
  return fetchWithFallback(`${API_BASE}/api/v1/segments/${segmentId}/shap`, () =>
    getMockShapContributions(segmentId),
  );
}

export async function fetchPrediction(segmentId: string) {
  return fetchWithFallback(`${API_BASE}/api/v1/segments/${segmentId}/prediction`, () =>
    getMockPrediction(segmentId),
  );
}

export async function postAiQuery(
  segmentId: string,
  question: string,
): Promise<{ answer: string }> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/assistant`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ segment_id: segmentId, question }),
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json() as Promise<{ answer: string }>;
  } catch {
    return {
      answer: `[Demo] Stub response. The AI assistant would analyze segment ${segmentId} and answer: "${question}". Connect the backend to enable real AI responses.`,
    };
  }
}
