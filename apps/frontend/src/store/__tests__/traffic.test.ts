import { useTrafficStore } from "../traffic";
import type { SegmentState, Alert, GlobalStats } from "@/lib/types";

const mockSegment: SegmentState = {
  id: "test-seg-01",
  name_en: "Test Road Seg 1",
  name_he: "כביש בדיקה 1",
  name_ar: "طريق اختبار 1",
  speed_limit: 50,
  live_speed: 40,
  status: "amber",
  geometry: [
    [31.77, 35.21],
    [31.78, 35.22],
  ],
  lat: 31.775,
  lng: 35.215,
  road: "test-road",
  seq: 1,
};

const mockAlert: Alert = {
  id: "alert-1",
  segment_id: "test-seg-01",
  segment_name: "Test Road Seg 1",
  type: "congestion",
  severity: "high",
  message: "Heavy congestion",
  timestamp: Date.now(),
  acknowledged: false,
};

const mockStats: GlobalStats = {
  avg_speed: 38.5,
  active_incidents: 2,
  segments_slow: 4,
  co2_saved: 100.0,
  total_segments: 42,
  timestamp: Date.now(),
};

describe("TrafficStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useTrafficStore.setState({
      segments: {},
      alerts: [],
      globalStats: null,
      usingMockData: true,
      timeTravelOffset: null,
    });
  });

  it("setSegments populates segments map", () => {
    useTrafficStore.getState().setSegments([mockSegment]);
    const state = useTrafficStore.getState();
    expect(state.segments["test-seg-01"]).toEqual(mockSegment);
  });

  it("updateSegment updates live speed and status", () => {
    useTrafficStore.getState().setSegments([mockSegment]);
    useTrafficStore.getState().updateSegment({
      segment_id: "test-seg-01",
      speed: 25,
      status: "red",
    });
    const seg = useTrafficStore.getState().segments["test-seg-01"];
    expect(seg.live_speed).toBe(25);
    expect(seg.status).toBe("red");
  });

  it("updateSegment does nothing for unknown segment", () => {
    useTrafficStore.getState().setSegments([mockSegment]);
    useTrafficStore.getState().updateSegment({
      segment_id: "nonexistent",
      speed: 10,
      status: "red",
    });
    expect(Object.keys(useTrafficStore.getState().segments)).toHaveLength(1);
  });

  it("addAlert prepends to alerts list", () => {
    useTrafficStore.getState().addAlert(mockAlert);
    expect(useTrafficStore.getState().alerts[0]).toEqual(mockAlert);
  });

  it("acknowledgeAlert marks alert as acknowledged", () => {
    useTrafficStore.getState().addAlert(mockAlert);
    useTrafficStore.getState().acknowledgeAlert("alert-1");
    expect(useTrafficStore.getState().alerts[0].acknowledged).toBe(true);
  });

  it("alerts list is capped at 50", () => {
    for (let i = 0; i < 55; i++) {
      useTrafficStore.getState().addAlert({ ...mockAlert, id: `alert-${i}` });
    }
    expect(useTrafficStore.getState().alerts.length).toBe(50);
  });

  it("setGlobalStats updates stats", () => {
    useTrafficStore.getState().setGlobalStats(mockStats);
    expect(useTrafficStore.getState().globalStats?.avg_speed).toBe(38.5);
  });

  it("setUsingMockData updates flag", () => {
    useTrafficStore.getState().setUsingMockData(false);
    expect(useTrafficStore.getState().usingMockData).toBe(false);
  });

  it("setTimeTravelOffset stores offset", () => {
    useTrafficStore.getState().setTimeTravelOffset(60);
    expect(useTrafficStore.getState().timeTravelOffset).toBe(60);
    useTrafficStore.getState().setTimeTravelOffset(null);
    expect(useTrafficStore.getState().timeTravelOffset).toBeNull();
  });
});
