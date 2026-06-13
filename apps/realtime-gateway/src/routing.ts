/** Pure mapping from Kafka messages to Socket.IO emissions.
 *
 * Kept side-effect free so the routing rules are unit-testable without a
 * broker or live sockets: given a topic and a raw message value, decide which
 * rooms get which event with what payload. The gateway layer performs the
 * actual `io.to(room).emit(...)`.
 */

export interface Emission {
  room: string;
  event: string;
  payload: unknown;
}

export const ALERTS_ROOM = "alerts";
export const GLOBAL_STATS_ROOM = "global-stats";

export function segmentRoom(segmentId: string): string {
  return `road-segment:${segmentId}`;
}

function parse(value: string | Buffer | null): Record<string, unknown> | null {
  if (value === null) return null;
  try {
    const parsed: unknown = JSON.parse(value.toString());
    return typeof parsed === "object" && parsed !== null
      ? (parsed as Record<string, unknown>)
      : null;
  } catch {
    return null;
  }
}

function segmentId(msg: Record<string, unknown>): string | undefined {
  const id = msg.segment_id ?? msg.segmentId;
  return typeof id === "string" ? id : undefined;
}

/** Map one Kafka record to zero or more socket emissions. */
export function routeMessage(topic: string, value: string | Buffer | null): Emission[] {
  const msg = parse(value);
  if (msg === null) return [];

  const seg = segmentId(msg);
  const emissions: Emission[] = [];

  switch (topic) {
    case "traffic.aggregates":
    case "traffic.events":
      if (seg) emissions.push({ room: segmentRoom(seg), event: "segment:update", payload: msg });
      break;
    case "vision.events":
      if (seg) emissions.push({ room: segmentRoom(seg), event: "segment:vision", payload: msg });
      break;
    case "predictions":
      if (seg)
        emissions.push({ room: segmentRoom(seg), event: "segment:prediction", payload: msg });
      break;
    case "alerts":
      emissions.push({ room: ALERTS_ROOM, event: "alert", payload: msg });
      // Alerts tied to a segment also reach that segment's subscribers.
      if (seg) emissions.push({ room: segmentRoom(seg), event: "segment:alert", payload: msg });
      break;
    default:
      break;
  }
  return emissions;
}

/** Rolling global statistics derived from the latest per-segment aggregates. */
export class GlobalStats {
  private readonly speedBySegment = new Map<string, number>();
  private activeAlerts = 0;

  ingest(topic: string, value: string | Buffer | null): void {
    const msg = parse(value);
    if (msg === null) return;
    if (topic === "traffic.aggregates" || topic === "traffic.events") {
      const seg = segmentId(msg);
      const speed = msg.avg_speed_kmh ?? msg.avgSpeedKmh;
      if (seg && typeof speed === "number") this.speedBySegment.set(seg, speed);
    } else if (topic === "alerts") {
      this.activeAlerts += 1;
    }
  }

  snapshot(): { segments: number; avgSpeedKmh: number; activeAlerts: number } {
    const speeds = [...this.speedBySegment.values()];
    const avg = speeds.length ? speeds.reduce((a, b) => a + b, 0) / speeds.length : 0;
    return {
      segments: this.speedBySegment.size,
      avgSpeedKmh: Math.round(avg * 10) / 10,
      activeAlerts: this.activeAlerts,
    };
  }
}
