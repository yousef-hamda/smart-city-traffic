/**
 * Mock data provider — generates Jerusalem segments from the real road network data
 * without requiring a backend. Mirrors the approach used in apps/frontend/src/lib/mock.ts.
 */

import { getSegmentStatus, type SegmentStatus } from "../utils/segmentColor";

export interface Coordinate {
  latitude: number;
  longitude: number;
}

export interface MobileSegment {
  id: string;
  name: string;
  coordinates: Coordinate[];
  currentSpeed: number;
  speedLimit: number;
  status: SegmentStatus;
}

export interface AuthResult {
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
  };
}

// Derived from scripts/seed/data/jerusalem_roads.json — real Jerusalem arteries
const ROAD_DATA = [
  {
    road: "jaffa-road",
    name_en: "Jaffa Road",
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
    speed_limit: 60,
    points: [
      [31.774, 35.18],
      [31.778, 35.186],
      [31.782, 35.192],
      [31.786, 35.2],
    ] as [number, number][],
  },
  {
    road: "salah-ad-din",
    name_en: "Salah ad-Din Street",
    speed_limit: 40,
    points: [
      [31.784, 35.229],
      [31.7865, 35.23],
      [31.789, 35.231],
    ] as [number, number][],
  },
  {
    road: "nablus-road",
    name_en: "Nablus Road",
    speed_limit: 50,
    points: [
      [31.782, 35.23],
      [31.79, 35.228],
      [31.796, 35.227],
    ] as [number, number][],
  },
  {
    road: "emek-refaim",
    name_en: "Emek Refaim Street",
    speed_limit: 40,
    points: [
      [31.766, 35.22],
      [31.762, 35.222],
      [31.758, 35.224],
    ] as [number, number][],
  },
  {
    road: "gaza-street",
    name_en: "Gaza Street",
    speed_limit: 40,
    points: [
      [31.771, 35.211],
      [31.7725, 35.2145],
      [31.774, 35.218],
    ] as [number, number][],
  },
  {
    road: "ramot-road",
    name_en: "Ramot Road",
    speed_limit: 70,
    points: [
      [31.815, 35.185],
      [31.82, 35.19],
      [31.825, 35.195],
    ] as [number, number][],
  },
  {
    road: "route-one-north",
    name_en: "Bar-Lev Road",
    speed_limit: 70,
    points: [
      [31.789, 35.226],
      [31.8, 35.23],
      [31.81, 35.233],
    ] as [number, number][],
  },
  {
    road: "kanfei-nesharim",
    name_en: "Kanfei Nesharim Street",
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
    speed_limit: 40,
    points: [
      [31.7765, 35.2235],
      [31.774, 35.2225],
      [31.771, 35.2215],
    ] as [number, number][],
  },
  {
    road: "keren-hayesod",
    name_en: "Keren HaYesod Street",
    speed_limit: 50,
    points: [
      [31.771, 35.2215],
      [31.7685, 35.2205],
      [31.766, 35.219],
    ] as [number, number][],
  },
  {
    road: "eshkol-boulevard",
    name_en: "Eshkol Boulevard",
    speed_limit: 60,
    points: [
      [31.799, 35.221],
      [31.803, 35.226],
      [31.806, 35.231],
    ] as [number, number][],
  },
  {
    road: "golomb-street",
    name_en: "Eliyahu Golomb Street",
    speed_limit: 50,
    points: [
      [31.762, 35.205],
      [31.757, 35.21],
      [31.752, 35.215],
    ] as [number, number][],
  },
] as const;

type RoadEntry = {
  readonly road: string;
  readonly name_en: string;
  readonly speed_limit: number;
  readonly points: readonly (readonly [number, number])[];
};

let _segments: MobileSegment[] | null = null;

function buildSegments(): MobileSegment[] {
  if (_segments) return _segments;

  const segs: MobileSegment[] = [];

  for (const road of ROAD_DATA as readonly RoadEntry[]) {
    const pts = road.points;
    for (let i = 0; i < pts.length - 1; i++) {
      const seq = i + 1;
      const id = `${road.road}-${String(seq).padStart(2, "0")}`;

      // Deterministic pseudo-random speed based on id character codes
      const hash = id.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
      const speedVariance = (hash % 40) - 20;
      const rawSpeed = road.speed_limit * 0.6 + speedVariance * 0.5;
      const currentSpeed = Math.max(5, Math.min(road.speed_limit, Math.round(rawSpeed)));

      const p0 = pts[i] as readonly [number, number];
      const p1 = pts[i + 1] as readonly [number, number];

      segs.push({
        id,
        name: `${road.name_en} Seg ${seq}`,
        coordinates: [
          { latitude: p0[0], longitude: p0[1] },
          { latitude: p1[0], longitude: p1[1] },
        ],
        currentSpeed,
        speedLimit: road.speed_limit,
        status: getSegmentStatus(currentSpeed, road.speed_limit),
      });
    }
  }

  _segments = segs;
  return segs;
}

export const mockSegments: MobileSegment[] = buildSegments();

export interface RouteResult {
  origin: string;
  destination: string;
  distanceKm: number;
  durationMin: number;
  segments: MobileSegment[];
}

export function mockRecommendRoute(origin: string, destination: string): RouteResult {
  // Pick the clearest-traffic segments as the "recommended" path
  const sorted = [...mockSegments].sort((a, b) => b.currentSpeed - a.currentSpeed);
  const routeSegments = sorted.slice(0, 5);
  const distanceKm = routeSegments.length * 0.8;
  const avgSpeed = routeSegments.reduce((s, seg) => s + seg.currentSpeed, 0) / routeSegments.length;
  const durationMin = Math.round((distanceKm / avgSpeed) * 60);

  return {
    origin,
    destination,
    distanceKm: Math.round(distanceKm * 10) / 10,
    durationMin,
    segments: routeSegments,
  };
}

export interface MockAuthResult extends AuthResult {}

export function mockAuth(email: string, _password: string, name?: string): AuthResult {
  const userId = `user-${email.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0)}`;
  const payload = JSON.stringify({ sub: userId, email });
  // Use btoa for base64 encoding (available in both browsers and React Native)
  const encoded = btoa(unescape(encodeURIComponent(payload)));
  return {
    token: `mock-jwt.${encoded}.signature`,
    user: {
      id: userId,
      email,
      name: name ?? email.split("@")[0] ?? "User",
    },
  };
}
