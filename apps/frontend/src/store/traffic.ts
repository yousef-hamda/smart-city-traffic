import { create } from "zustand";
import type { SegmentState, Alert, GlobalStats } from "@/lib/types";

interface TrafficStore {
  segments: Record<string, SegmentState>;
  alerts: Alert[];
  globalStats: GlobalStats | null;
  usingMockData: boolean;
  timeTravelOffset: number | null; // null = live, minutes offset = past

  setSegments: (segments: SegmentState[]) => void;
  updateSegment: (update: {
    segment_id: string;
    speed: number;
    status: SegmentState["status"];
  }) => void;
  addAlert: (alert: Alert) => void;
  acknowledgeAlert: (alertId: string) => void;
  setGlobalStats: (stats: GlobalStats) => void;
  setUsingMockData: (value: boolean) => void;
  setTimeTravelOffset: (offset: number | null) => void;
}

export const useTrafficStore = create<TrafficStore>((set) => ({
  segments: {},
  alerts: [],
  globalStats: null,
  usingMockData: true,
  timeTravelOffset: null,

  setSegments: (segments) => set({ segments: Object.fromEntries(segments.map((s) => [s.id, s])) }),

  updateSegment: (update) =>
    set((state) => {
      const existing = state.segments[update.segment_id];
      if (!existing) return state;
      return {
        segments: {
          ...state.segments,
          [update.segment_id]: {
            ...existing,
            live_speed: update.speed,
            status: update.status,
          },
        },
      };
    }),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts].slice(0, 50),
    })),

  acknowledgeAlert: (alertId) =>
    set((state) => ({
      alerts: state.alerts.map((a) => (a.id === alertId ? { ...a, acknowledged: true } : a)),
    })),

  setGlobalStats: (stats) => set({ globalStats: stats }),
  setUsingMockData: (value) => set({ usingMockData: value }),
  setTimeTravelOffset: (offset) => set({ timeTravelOffset: offset }),
}));
