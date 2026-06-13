export type SegmentStatus = "green" | "amber" | "red" | "unknown";

export interface SegmentState {
  id: string;
  name_en: string;
  name_he: string;
  name_ar: string;
  speed_limit: number;
  live_speed: number;
  status: SegmentStatus;
  geometry: [number, number][]; // [lat, lng] pairs
  lat: number;
  lng: number;
  road: string;
  seq: number;
}

export interface Alert {
  id: string;
  segment_id: string;
  segment_name: string;
  type: "congestion" | "incident" | "roadwork" | "weather";
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  timestamp: number;
  acknowledged: boolean;
}

export interface GlobalStats {
  avg_speed: number;
  active_incidents: number;
  segments_slow: number;
  co2_saved: number;
  total_segments: number;
  timestamp: number;
}

export interface SegmentUpdate {
  segment_id: string;
  speed: number;
  status: SegmentStatus;
  timestamp: number;
}

export interface SegmentPrediction {
  segment_id: string;
  predicted_speed: number;
  confidence: number;
  horizon_minutes: number;
  confidence_band: { upper: number; lower: number }[];
  timestamp: number;
}

export interface SegmentHistory {
  segment_id: string;
  timestamps: number[];
  speeds: number[];
  statuses: SegmentStatus[];
}

export interface ShapContribution {
  feature: string;
  value: number;
  impact: number;
}

export interface ScenarioResult {
  segment_id: string;
  predicted_speed_change: number;
  predicted_status: SegmentStatus;
  impact_magnitude: number;
}
