/**
 * Returns a color string based on how congested a road segment is.
 *
 * free:     currentSpeed >= speedLimit * 0.7  → green
 * moderate: currentSpeed >= speedLimit * 0.3  → amber
 * congested: below 30% of speed limit         → red
 */
export type SegmentStatus = "free" | "moderate" | "congested";

export function getSegmentStatus(currentSpeed: number, speedLimit: number): SegmentStatus {
  const ratio = currentSpeed / speedLimit;
  if (ratio >= 0.7) return "free";
  if (ratio >= 0.3) return "moderate";
  return "congested";
}

export function getSegmentColor(currentSpeed: number, speedLimit: number): string {
  const status = getSegmentStatus(currentSpeed, speedLimit);
  switch (status) {
    case "free":
      return "#22c55e";
    case "moderate":
      return "#f59e0b";
    case "congested":
      return "#ef4444";
  }
}
