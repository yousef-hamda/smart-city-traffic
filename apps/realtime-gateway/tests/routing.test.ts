import { ALERTS_ROOM, GlobalStats, routeMessage, segmentRoom } from "../src/routing";

const json = (o: unknown): string => JSON.stringify(o);

describe("routeMessage", () => {
  it("routes aggregates to the segment room", () => {
    const out = routeMessage(
      "traffic.aggregates",
      json({ segment_id: "jaffa-road-00", avg_speed_kmh: 30 }),
    );
    expect(out).toEqual([
      { room: segmentRoom("jaffa-road-00"), event: "segment:update", payload: expect.any(Object) },
    ]);
  });

  it("routes vision events to a vision event", () => {
    const out = routeMessage("vision.events", json({ segment_id: "jaffa-road-01" }));
    expect(out[0]).toMatchObject({ room: segmentRoom("jaffa-road-01"), event: "segment:vision" });
  });

  it("routes predictions", () => {
    const out = routeMessage("predictions", json({ segment_id: "x", predicted_speed_kmh: 22 }));
    expect(out[0].event).toBe("segment:prediction");
  });

  it("fans an alert to both the alerts room and the segment room", () => {
    const out = routeMessage("alerts", json({ segment_id: "x", message: "stopped vehicle" }));
    const rooms = out.map((e) => e.room);
    expect(rooms).toContain(ALERTS_ROOM);
    expect(rooms).toContain(segmentRoom("x"));
  });

  it("emits a global alert with no segment", () => {
    const out = routeMessage("alerts", json({ message: "network-wide" }));
    expect(out).toEqual([{ room: ALERTS_ROOM, event: "alert", payload: expect.any(Object) }]);
  });

  it("ignores unknown topics and malformed payloads", () => {
    expect(routeMessage("nope", json({ segment_id: "x" }))).toEqual([]);
    expect(routeMessage("alerts", "not-json")).toEqual([]);
    expect(routeMessage("alerts", null)).toEqual([]);
  });
});

describe("GlobalStats", () => {
  it("averages segment speeds and counts alerts", () => {
    const stats = new GlobalStats();
    stats.ingest("traffic.aggregates", json({ segment_id: "a", avg_speed_kmh: 20 }));
    stats.ingest("traffic.aggregates", json({ segment_id: "b", avg_speed_kmh: 40 }));
    stats.ingest("alerts", json({ message: "x" }));
    expect(stats.snapshot()).toEqual({ segments: 2, avgSpeedKmh: 30, activeAlerts: 1 });
  });

  it("keeps only the latest speed per segment", () => {
    const stats = new GlobalStats();
    stats.ingest("traffic.aggregates", json({ segment_id: "a", avg_speed_kmh: 20 }));
    stats.ingest("traffic.aggregates", json({ segment_id: "a", avg_speed_kmh: 50 }));
    expect(stats.snapshot()).toEqual({ segments: 1, avgSpeedKmh: 50, activeAlerts: 0 });
  });
});
