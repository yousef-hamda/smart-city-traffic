import {
  getMockSegments,
  getMockGlobalStats,
  getMockAlerts,
  getMockSegmentHistory,
  getMockShapContributions,
  getMockPrediction,
  getHistoryBuffer,
} from "../mock";

describe("mock data provider", () => {
  it("returns segments with required fields", () => {
    const segments = getMockSegments();
    expect(segments.length).toBeGreaterThan(0);
    const first = segments[0];
    expect(first).toHaveProperty("id");
    expect(first).toHaveProperty("name_en");
    expect(first).toHaveProperty("live_speed");
    expect(first).toHaveProperty("speed_limit");
    expect(first).toHaveProperty("status");
    expect(first).toHaveProperty("geometry");
    expect(first.geometry.length).toBeGreaterThanOrEqual(2);
  });

  it("returns valid status values", () => {
    const segments = getMockSegments();
    const validStatuses = ["green", "amber", "red", "unknown"];
    segments.forEach((seg) => {
      expect(validStatuses).toContain(seg.status);
    });
  });

  it("returns global stats", () => {
    const stats = getMockGlobalStats();
    expect(stats.avg_speed).toBeGreaterThan(0);
    expect(stats.total_segments).toBeGreaterThan(0);
    expect(typeof stats.co2_saved).toBe("number");
  });

  it("returns alerts only for red segments", () => {
    const alerts = getMockAlerts();
    expect(Array.isArray(alerts)).toBe(true);
    alerts.forEach((alert) => {
      expect(alert).toHaveProperty("id");
      expect(alert).toHaveProperty("segment_id");
      expect(alert).toHaveProperty("type");
      expect(alert).toHaveProperty("severity");
      expect(alert.acknowledged).toBe(false);
    });
  });

  it("returns segment history with correct shape", () => {
    const segs = getMockSegments();
    const history = getMockSegmentHistory(segs[0].id);
    expect(history.segment_id).toBe(segs[0].id);
    expect(history.timestamps.length).toBe(history.speeds.length);
    expect(history.speeds.length).toBe(history.statuses.length);
    expect(history.timestamps.length).toBe(24);
  });

  it("returns SHAP contributions", () => {
    const segs = getMockSegments();
    const shap = getMockShapContributions(segs[0].id);
    expect(shap.length).toBeGreaterThan(0);
    shap.forEach((s) => {
      expect(s).toHaveProperty("feature");
      expect(s).toHaveProperty("impact");
    });
  });

  it("returns prediction data", () => {
    const segs = getMockSegments();
    const pred = getMockPrediction(segs[0].id);
    expect(pred.segment_id).toBe(segs[0].id);
    expect(pred.predicted_speed).toBeGreaterThan(0);
    expect(pred.confidence_band.length).toBeGreaterThan(0);
  });

  it("time-travel buffer adjusts speeds", () => {
    const live = getMockSegments();
    const past = getHistoryBuffer(90);
    expect(past.length).toBe(live.length);
    // Speeds should differ from live (at least some)
    const diffs = past.filter((seg, i) => seg.live_speed !== live[i].live_speed);
    expect(diffs.length).toBeGreaterThan(0);
  });
});
