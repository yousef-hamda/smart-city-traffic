import { getSegmentColor, getSegmentStatus } from "../src/utils/segmentColor";

describe("getSegmentStatus", () => {
  it("returns free for fast traffic (>= 70% of speed limit)", () => {
    expect(getSegmentStatus(50, 50)).toBe("free");
    expect(getSegmentStatus(35, 50)).toBe("free");
    expect(getSegmentStatus(70, 100)).toBe("free");
  });

  it("returns moderate for medium traffic (>= 30% and < 70% of speed limit)", () => {
    expect(getSegmentStatus(20, 50)).toBe("moderate");
    expect(getSegmentStatus(30, 100)).toBe("moderate");
    expect(getSegmentStatus(34, 50)).toBe("moderate");
  });

  it("returns congested for slow traffic (< 30% of speed limit)", () => {
    expect(getSegmentStatus(10, 50)).toBe("congested");
    expect(getSegmentStatus(5, 60)).toBe("congested");
    expect(getSegmentStatus(0, 80)).toBe("congested");
  });
});

describe("getSegmentColor", () => {
  it("returns green (#22c55e) for free traffic", () => {
    expect(getSegmentColor(50, 50)).toBe("#22c55e");
  });

  it("returns amber (#f59e0b) for moderate traffic", () => {
    expect(getSegmentColor(20, 50)).toBe("#f59e0b");
  });

  it("returns red (#ef4444) for congested traffic", () => {
    expect(getSegmentColor(10, 50)).toBe("#ef4444");
  });

  it("handles edge case at exactly 70% boundary (free)", () => {
    // 35/50 = 0.7 exactly -> free
    expect(getSegmentColor(35, 50)).toBe("#22c55e");
  });

  it("handles edge case at exactly 30% boundary (moderate)", () => {
    // 15/50 = 0.3 exactly -> moderate
    expect(getSegmentColor(15, 50)).toBe("#f59e0b");
  });
});
