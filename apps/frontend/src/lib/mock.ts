// Mock data provider — generates Jerusalem segments from actual road network data
// without requiring a backend. Uses real coordinates from jerusalem_roads.json.

import type { SegmentState, Alert, GlobalStats, SegmentHistory, ShapContribution } from "./types";

// Derived from scripts/seed/data/jerusalem_roads.json — real Jerusalem arteries
const ROAD_DATA = [
  {
    road: "jaffa-road",
    name_en: "Jaffa Road",
    name_he: "רחוב יפו",
    name_ar: "شارع يافا",
    speed_limit: 50,
    points: [
      [31.7767, 35.2274],
      [31.7795, 35.2225],
      [31.7812, 35.2186],
      [31.7842, 35.213],
      [31.7857, 35.209],
      [31.7894, 35.2026],
    ] as [number, number][],
  },
  {
    road: "king-george",
    name_en: "King George Street",
    name_he: "רחוב המלך ג'ורג'",
    name_ar: "شارع الملك جورج",
    speed_limit: 50,
    points: [
      [31.7712, 35.2188],
      [31.7745, 35.2165],
      [31.7775, 35.2152],
      [31.7812, 35.2138],
    ] as [number, number][],
  },
  {
    road: "agripas",
    name_en: "Agripas Street",
    name_he: "רחוב אגריפס",
    name_ar: "شارع أغريباس",
    speed_limit: 40,
    points: [
      [31.7843, 35.212],
      [31.7826, 35.2148],
      [31.7809, 35.2169],
      [31.7795, 35.2185],
    ] as [number, number][],
  },
  {
    road: "hebron-road",
    name_en: "Hebron Road",
    name_he: "דרך חברון",
    name_ar: "طريق الخليل",
    speed_limit: 60,
    points: [
      [31.77, 35.228],
      [31.764, 35.2265],
      [31.757, 35.225],
      [31.752, 35.224],
      [31.748, 35.223],
    ] as [number, number][],
  },
  {
    road: "begin-boulevard",
    name_en: "Menachem Begin Boulevard",
    name_he: "שדרות מנחם בגין",
    name_ar: "جادة مناحم بيغن",
    speed_limit: 80,
    points: [
      [31.805, 35.2],
      [31.795, 35.1985],
      [31.785, 35.197],
      [31.77, 35.194],
      [31.76, 35.1945],
      [31.75, 35.195],
    ] as [number, number][],
  },
  {
    road: "golda-meir",
    name_en: "Golda Meir Boulevard",
    name_he: "שדרות גולדה מאיר",
    name_ar: "جادة غولدا مئير",
    speed_limit: 70,
    points: [
      [31.795, 35.205],
      [31.802, 35.199],
      [31.808, 35.193],
      [31.815, 35.185],
    ] as [number, number][],
  },
  {
    road: "herzl-boulevard",
    name_en: "Herzl Boulevard",
    name_he: "שדרות הרצל",
    name_ar: "جادة هرتسل",
    speed_limit: 60,
    points: [
      [31.774, 35.18],
      [31.778, 35.186],
      [31.782, 35.192],
      [31.786, 35.2],
    ] as [number, number][],
  },
  {
    road: "emek-refaim",
    name_en: "Emek Refaim Street",
    name_he: "רחוב עמק רפאים",
    name_ar: "شارع عيمك ريفايم",
    speed_limit: 40,
    points: [
      [31.766, 35.22],
      [31.762, 35.222],
      [31.758, 35.224],
    ] as [number, number][],
  },
  {
    road: "kanfei-nesharim",
    name_en: "Kanfei Nesharim Street",
    name_he: "רחוב כנפי נשרים",
    name_ar: "شارع كنفي نشاريم",
    speed_limit: 50,
    points: [
      [31.79, 35.18],
      [31.7925, 35.186],
      [31.795, 35.192],
      [31.796, 35.198],
    ] as [number, number][],
  },
  {
    road: "king-david",
    name_en: "King David Street",
    name_he: "רחוב המלך דוד",
    name_ar: "شارع الملك داود",
    speed_limit: 40,
    points: [
      [31.7765, 35.2235],
      [31.774, 35.2225],
      [31.771, 35.2215],
    ] as [number, number][],
  },
  {
    road: "nablus-road",
    name_en: "Nablus Road",
    name_he: "דרך שכם",
    name_ar: "طريق نابلس",
    speed_limit: 50,
    points: [
      [31.782, 35.23],
      [31.79, 35.228],
      [31.796, 35.227],
    ] as [number, number][],
  },
] as const;

type RoadEntry = {
  road: string;
  name_en: string;
  name_he: string;
  name_ar: string;
  speed_limit: number;
  points: readonly (readonly [number, number])[];
};

function computeStatus(speed: number, limit: number): "green" | "amber" | "red" {
  const ratio = speed / limit;
  if (ratio >= 0.7) return "green";
  if (ratio >= 0.4) return "amber";
  return "red";
}

let _segments: SegmentState[] | null = null;

function buildSegments(): SegmentState[] {
  if (_segments) return _segments;
  const segs: SegmentState[] = [];
  for (const road of ROAD_DATA as readonly RoadEntry[]) {
    const pts = road.points as readonly (readonly [number, number])[];
    for (let i = 0; i < pts.length - 1; i++) {
      const seq = i + 1;
      const id = `${road.road}-${String(seq).padStart(2, "0")}`;
      // Deterministic pseudo-random speed based on id character codes
      const hash = id.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
      const speedVariance = (hash % 40) - 20;
      const liveSpeed = Math.max(
        5,
        Math.min(road.speed_limit, road.speed_limit * 0.6 + speedVariance * 0.5),
      );
      const p0 = pts[i] as [number, number];
      const p1 = pts[i + 1] as [number, number];
      segs.push({
        id,
        name_en: `${road.name_en} Seg ${seq}`,
        name_he: `${road.name_he} קטע ${seq}`,
        name_ar: `${road.name_ar} قسم ${seq}`,
        speed_limit: road.speed_limit,
        live_speed: Math.round(liveSpeed),
        status: computeStatus(liveSpeed, road.speed_limit),
        geometry: [p0, p1],
        lat: (p0[0] + p1[0]) / 2,
        lng: (p0[1] + p1[1]) / 2,
        road: road.road,
        seq,
      });
    }
  }
  _segments = segs;
  return segs;
}

export function getMockSegments(): SegmentState[] {
  return buildSegments();
}

export function getMockGlobalStats(): GlobalStats {
  const segs = buildSegments();
  const avgSpeed = segs.reduce((sum, s) => sum + s.live_speed, 0) / segs.length;
  const slow = segs.filter((s) => s.status === "red").length;
  return {
    avg_speed: Math.round(avgSpeed * 10) / 10,
    active_incidents: 3,
    segments_slow: slow,
    co2_saved: 142.7,
    total_segments: segs.length,
    timestamp: Date.now(),
  };
}

const ALERT_TEMPLATES: Array<{
  type: Alert["type"];
  message: string;
  severity: Alert["severity"];
}> = [
  { type: "congestion", message: "Heavy congestion detected", severity: "high" },
  { type: "incident", message: "Traffic incident reported", severity: "critical" },
  { type: "roadwork", message: "Roadwork in progress", severity: "medium" },
  { type: "weather", message: "Reduced visibility due to weather", severity: "low" },
];

export function getMockAlerts(): Alert[] {
  const segs = buildSegments();
  const redSegs = segs.filter((s) => s.status === "red").slice(0, 5);
  return redSegs.map((seg, i) => {
    const tpl = ALERT_TEMPLATES[i % ALERT_TEMPLATES.length];
    return {
      id: `alert-${i + 1}`,
      segment_id: seg.id,
      segment_name: seg.name_en,
      type: tpl.type,
      severity: tpl.severity,
      message: `${tpl.message} on ${seg.name_en}`,
      timestamp: Date.now() - i * 60000,
      acknowledged: false,
    };
  });
}

export function getMockSegmentHistory(segmentId: string): SegmentHistory {
  const seg = buildSegments().find((s) => s.id === segmentId);
  const now = Date.now();
  const count = 24;
  const timestamps = Array.from({ length: count }, (_, i) => now - (count - i) * 3600000);
  const hash = segmentId.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const baseSpeed = seg?.live_speed ?? 40;
  const speeds = timestamps.map((_, i) => {
    const hourVariance = Math.sin(((i + (hash % 6)) * Math.PI) / 6) * 15;
    return Math.max(5, Math.round(baseSpeed + hourVariance));
  });
  const statuses = speeds.map((s) => computeStatus(s, seg?.speed_limit ?? 50));
  return { segment_id: segmentId, timestamps, speeds, statuses };
}

export function getMockShapContributions(segmentId: string): ShapContribution[] {
  const hash = segmentId.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const features = [
    "Time of day",
    "Adjacent segments",
    "Historical pattern",
    "Weather",
    "Day of week",
  ];
  return features.map((feature, i) => ({
    feature,
    value: ((hash + i * 17) % 100) / 100,
    impact: (((hash + i * 13) % 60) - 30) / 10,
  }));
}

export function getMockPrediction(segmentId: string) {
  const seg = buildSegments().find((s) => s.id === segmentId);
  const baseSpeed = seg?.live_speed ?? 40;
  const band = Array.from({ length: 12 }, (_, i) => {
    const drift = i * 1.5;
    return {
      upper: Math.round(baseSpeed + drift + 5),
      lower: Math.round(Math.max(5, baseSpeed - drift)),
    };
  });
  return {
    segment_id: segmentId,
    predicted_speed: Math.round(baseSpeed * 1.1),
    confidence: 0.82,
    horizon_minutes: 60,
    confidence_band: band,
    timestamp: Date.now(),
  };
}

export function getHistoryBuffer(offsetMinutes: number): SegmentState[] {
  const segs = buildSegments();
  const factor = 1 + Math.sin((offsetMinutes * Math.PI) / 180) * 0.3;
  return segs.map((seg) => {
    const adjustedSpeed = Math.max(
      5,
      Math.min(seg.speed_limit, Math.round(seg.live_speed * factor)),
    );
    return {
      ...seg,
      live_speed: adjustedSpeed,
      status: computeStatus(adjustedSpeed, seg.speed_limit),
    };
  });
}
