import { z } from "zod";

export const SegmentStatusSchema = z.enum(["green", "amber", "red", "unknown"]);

export const SegmentUpdateSchema = z.object({
  segment_id: z.string(),
  speed: z.number(),
  status: SegmentStatusSchema,
  timestamp: z.number(),
});

export const AlertSchema = z.object({
  id: z.string(),
  segment_id: z.string(),
  segment_name: z.string(),
  type: z.enum(["congestion", "incident", "roadwork", "weather"]),
  severity: z.enum(["low", "medium", "high", "critical"]),
  message: z.string(),
  timestamp: z.number(),
  acknowledged: z.boolean().default(false),
});

export const GlobalStatsSchema = z.object({
  avg_speed: z.number(),
  active_incidents: z.number(),
  segments_slow: z.number(),
  co2_saved: z.number(),
  total_segments: z.number(),
  timestamp: z.number(),
});
