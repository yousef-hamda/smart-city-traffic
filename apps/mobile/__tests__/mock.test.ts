import { mockSegments, mockAuth, mockRecommendRoute } from "../src/lib/mock";

describe("mockSegments", () => {
  it("has between 40 and 55 segments (approximately 49)", () => {
    expect(mockSegments.length).toBeGreaterThanOrEqual(40);
    expect(mockSegments.length).toBeLessThanOrEqual(55);
  });

  it("each segment has all required fields", () => {
    for (const seg of mockSegments) {
      expect(seg).toHaveProperty("id");
      expect(typeof seg.id).toBe("string");
      expect(seg.id.length).toBeGreaterThan(0);

      expect(seg).toHaveProperty("name");
      expect(typeof seg.name).toBe("string");

      expect(seg).toHaveProperty("coordinates");
      expect(Array.isArray(seg.coordinates)).toBe(true);
      expect(seg.coordinates.length).toBeGreaterThanOrEqual(2);

      for (const coord of seg.coordinates) {
        expect(coord).toHaveProperty("latitude");
        expect(coord).toHaveProperty("longitude");
        expect(typeof coord.latitude).toBe("number");
        expect(typeof coord.longitude).toBe("number");
      }

      expect(seg).toHaveProperty("currentSpeed");
      expect(typeof seg.currentSpeed).toBe("number");
      expect(seg.currentSpeed).toBeGreaterThan(0);

      expect(seg).toHaveProperty("speedLimit");
      expect(typeof seg.speedLimit).toBe("number");
      expect(seg.speedLimit).toBeGreaterThan(0);

      expect(seg).toHaveProperty("status");
      expect(["free", "moderate", "congested"]).toContain(seg.status);
    }
  });

  it("has unique ids", () => {
    const ids = mockSegments.map((s) => s.id);
    const uniqueIds = new Set(ids);
    expect(uniqueIds.size).toBe(ids.length);
  });

  it("coordinates are in Jerusalem area", () => {
    for (const seg of mockSegments) {
      for (const coord of seg.coordinates) {
        // Jerusalem is roughly lat 31.7-31.9, lng 35.1-35.3
        expect(coord.latitude).toBeGreaterThan(31.7);
        expect(coord.latitude).toBeLessThan(31.9);
        expect(coord.longitude).toBeGreaterThan(35.1);
        expect(coord.longitude).toBeLessThan(35.3);
      }
    }
  });
});

describe("mockAuth", () => {
  it("returns a token and user for valid credentials", () => {
    const result = mockAuth("test@example.com", "password123");
    expect(result).toHaveProperty("token");
    expect(typeof result.token).toBe("string");
    expect(result.token.length).toBeGreaterThan(0);
    expect(result).toHaveProperty("user");
    expect(result.user.email).toBe("test@example.com");
  });

  it("token has three parts (JWT-like format)", () => {
    const result = mockAuth("user@test.com", "pass");
    const parts = result.token.split(".");
    expect(parts.length).toBe(3);
  });

  it("uses provided name when given", () => {
    const result = mockAuth("jane@test.com", "pass", "Jane Doe");
    expect(result.user.name).toBe("Jane Doe");
  });

  it("derives name from email when not provided", () => {
    const result = mockAuth("alice@example.com", "pass");
    expect(result.user.name).toBe("alice");
  });
});

describe("mockRecommendRoute", () => {
  it("returns origin and destination", () => {
    const result = mockRecommendRoute("City Center", "Talpiot");
    expect(result.origin).toBe("City Center");
    expect(result.destination).toBe("Talpiot");
  });

  it("returns numeric distance and duration", () => {
    const result = mockRecommendRoute("A", "B");
    expect(typeof result.distanceKm).toBe("number");
    expect(result.distanceKm).toBeGreaterThan(0);
    expect(typeof result.durationMin).toBe("number");
    expect(result.durationMin).toBeGreaterThan(0);
  });

  it("returns route segments", () => {
    const result = mockRecommendRoute("A", "B");
    expect(Array.isArray(result.segments)).toBe(true);
    expect(result.segments.length).toBeGreaterThan(0);
  });
});
