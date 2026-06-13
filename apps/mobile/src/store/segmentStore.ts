/**
 * Zustand segment store.
 * Fetches road segments from the API, caches them in AsyncStorage,
 * and loads from cache when offline.
 */

import { create } from "zustand";
import * as api from "../lib/api";
import { saveSegments, loadSegments } from "../lib/storage";
import type { MobileSegment } from "../lib/mock";

export interface SegmentState {
  segments: MobileSegment[];
  isOffline: boolean;
  lastUpdated: number | null;
  isLoading: boolean;
  error: string | null;
}

export interface SegmentActions {
  fetchSegments: () => Promise<void>;
  refreshSegments: () => Promise<void>;
}

export type SegmentStore = SegmentState & SegmentActions;

async function loadFromNetworkOrCache(): Promise<{
  segments: MobileSegment[];
  isOffline: boolean;
}> {
  try {
    const segments = await api.getSegments();
    // Persist to cache for offline use
    await saveSegments(segments).catch(() => undefined);
    return { segments, isOffline: false };
  } catch {
    // Network failed — try cache
    const cached = await loadSegments();
    if (cached && cached.length > 0) {
      return { segments: cached, isOffline: true };
    }
    // No cache either — return empty
    return { segments: [], isOffline: true };
  }
}

export const useSegmentStore = create<SegmentStore>((set, get) => ({
  segments: [],
  isOffline: false,
  lastUpdated: null,
  isLoading: false,
  error: null,

  fetchSegments: async () => {
    // Skip if we already have segments and are not stale
    if (get().segments.length > 0 && get().lastUpdated !== null) return;
    set({ isLoading: true, error: null });
    try {
      const { segments, isOffline } = await loadFromNetworkOrCache();
      set({ segments, isOffline, lastUpdated: Date.now(), isLoading: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load segments";
      set({ isLoading: false, error: message });
    }
  },

  refreshSegments: async () => {
    set({ isLoading: true, error: null });
    try {
      const { segments, isOffline } = await loadFromNetworkOrCache();
      set({ segments, isOffline, lastUpdated: Date.now(), isLoading: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to refresh segments";
      set({ isLoading: false, error: message });
    }
  },
}));
