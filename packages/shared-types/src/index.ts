import { z } from 'zod';

/* ------------------------------------------------------------------------ *
 * Roles
 * ------------------------------------------------------------------------ */

export type UserRole = 'admin' | 'analyst' | 'viewer' | 'citizen';

export const USER_ROLES: readonly UserRole[] = ['admin', 'analyst', 'viewer', 'citizen'];

/* ------------------------------------------------------------------------ *
 * Sensor readings
 * ------------------------------------------------------------------------ */

export const SensorReadingSchema = z.object({
  /** Stable identifier of the road sensor. */
  sensorId: z.string().min(1),
  /** Reading timestamp, ISO-8601 UTC. */
  ts: z.string().datetime(),
  lat: z.number().min(-90).max(90),
  lon: z.number().min(-180).max(180),
  /** Vehicles counted during the aggregation window. */
  vehicleCount: z.number().int().nonnegative(),
  /** Average speed over the window, km/h. */
  avgSpeedKmh: z.number().nonnegative(),
  /** Lane occupancy, 0–100. */
  occupancyPct: z.number().min(0).max(100),
});

export type SensorReading = z.infer<typeof SensorReadingSchema>;

/* ------------------------------------------------------------------------ *
 * Computer-vision events
 * ------------------------------------------------------------------------ */

export type VisionEventType =
  | 'vehicle_detected'
  | 'pedestrian_detected'
  | 'collision_suspected'
  | 'wrong_way_driver'
  | 'stopped_vehicle';

export interface VisionEvent {
  eventId: string;
  cameraId: string;
  /** Event timestamp, ISO-8601 UTC. */
  ts: string;
  type: VisionEventType;
  /** Detection confidence in [0, 1]. */
  confidence: number;
  lat: number;
  lon: number;
  /** Optional bounding box in frame pixel coordinates. */
  bbox?: { x: number; y: number; width: number; height: number };
}

/* ------------------------------------------------------------------------ *
 * ML predictions
 * ------------------------------------------------------------------------ */

/** Single SHAP feature attribution. */
export interface ShapAttribution {
  feature: string;
  value: number;
}

export interface Prediction {
  predictionId: string;
  segmentId: string;
  /** Time the prediction was produced, ISO-8601 UTC. */
  ts: string;
  /** Forecast horizon in minutes (e.g. 15, 30, 60). */
  horizonMinutes: number;
  /** Predicted congestion level in [0, 1]. */
  congestionScore: number;
  predictedAvgSpeedKmh: number;
  /** Identifier/version of the model that produced this prediction. */
  modelVersion: string;
  /** Top 5 SHAP feature attributions explaining the prediction. */
  shapTop5: ShapAttribution[];
}

/* ------------------------------------------------------------------------ *
 * Incidents & alerts
 * ------------------------------------------------------------------------ */

export const INCIDENT_TYPES = [
  'accident',
  'congestion',
  'road_closure',
  'roadwork',
  'weather',
  'special_event',
] as const;

export const INCIDENT_SEVERITIES = ['low', 'medium', 'high', 'critical'] as const;

export const INCIDENT_STATUSES = ['open', 'acknowledged', 'resolved'] as const;

export const IncidentSchema = z.object({
  incidentId: z.string().min(1),
  segmentId: z.string().min(1),
  type: z.enum(INCIDENT_TYPES),
  severity: z.enum(INCIDENT_SEVERITIES),
  status: z.enum(INCIDENT_STATUSES),
  /** Incident start, ISO-8601 UTC. */
  startedAt: z.string().datetime(),
  /** Set when status becomes "resolved". */
  resolvedAt: z.string().datetime().optional(),
  lat: z.number().min(-90).max(90),
  lon: z.number().min(-180).max(180),
  description: z.string().optional(),
});

export type Incident = z.infer<typeof IncidentSchema>;

export type IncidentType = Incident['type'];
export type IncidentSeverity = Incident['severity'];
export type IncidentStatus = Incident['status'];

export interface Alert {
  alertId: string;
  /** Incident that triggered the alert, if any. */
  incidentId?: string;
  segmentId: string;
  severity: IncidentSeverity;
  /** Alert creation time, ISO-8601 UTC. */
  createdAt: string;
  /** i18n message key (catalogs live in @smart-city/i18n). */
  messageKey: string;
  acknowledged: boolean;
  acknowledgedBy?: string;
}

/* ------------------------------------------------------------------------ *
 * Road network
 * ------------------------------------------------------------------------ */

export interface RoadSegment {
  segmentId: string;
  /** Multilingual display names. */
  nameEn: string;
  nameHe: string;
  nameAr: string;
  /** Ordered polyline as [lon, lat] pairs (GeoJSON-style). */
  geometry: Array<[number, number]>;
  lengthMeters: number;
  lanes: number;
  speedLimitKmh: number;
}
