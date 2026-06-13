import { cn, getStatusColor, getStatusBgClass, formatSpeed, formatTimestamp } from "../utils";

describe("cn utility", () => {
  it("merges class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("deduplicates tailwind classes", () => {
    expect(cn("p-2", "p-4")).toBe("p-4");
  });

  it("handles falsy values", () => {
    expect(cn("foo", false && "bar", undefined, null as unknown as string, "baz")).toBe("foo baz");
  });
});

describe("getStatusColor", () => {
  it("returns green color for green status", () => {
    expect(getStatusColor("green")).toBe("#22c55e");
  });

  it("returns amber color for amber status", () => {
    expect(getStatusColor("amber")).toBe("#f59e0b");
  });

  it("returns red color for red status", () => {
    expect(getStatusColor("red")).toBe("#ef4444");
  });

  it("returns slate for unknown status", () => {
    expect(getStatusColor("unknown")).toBe("#64748b");
  });
});

describe("getStatusBgClass", () => {
  it("returns correct class for green", () => {
    expect(getStatusBgClass("green")).toContain("green");
  });

  it("returns correct class for red", () => {
    expect(getStatusBgClass("red")).toContain("red");
  });
});

describe("formatSpeed", () => {
  it("appends km/h unit", () => {
    expect(formatSpeed(50)).toBe("50 km/h");
  });
});

describe("formatTimestamp", () => {
  it("returns a non-empty string for a valid timestamp", () => {
    const result = formatTimestamp(Date.now());
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });
});
