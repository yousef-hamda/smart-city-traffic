"""Incident detection from confirmed tracks.

These run on the tracker output, so they work identically for synthetic and
YOLO detections:

- **stopped vehicle** — a confirmed track whose center barely moves over the
  last ``stopped_seconds`` of frames (default 30 s).
- **wrong-way** — a track whose horizontal velocity opposes the prevailing
  flow (median velocity of the other confirmed tracks) with enough magnitude.
- **sudden lane change** — a large vertical displacement (relative to the
  vehicle's height) over a short window.
"""

from dataclasses import dataclass
from enum import StrEnum
from statistics import median

from vision_service.tracking import Track


class IncidentKind(StrEnum):
    STOPPED_VEHICLE = "stopped_vehicle"
    WRONG_WAY = "wrong_way"
    SUDDEN_LANE_CHANGE = "sudden_lane_change"


@dataclass(frozen=True)
class Incident:
    kind: IncidentKind
    track_id: int
    label: str
    confidence: float


@dataclass
class IncidentDetector:
    fps: float
    stopped_seconds: float = 30.0
    stopped_pixel_eps: float = 6.0
    wrong_way_min_speed: float = 1.5
    lane_change_window: int = 8
    lane_change_ratio: float = 1.2

    def _stopped_window(self) -> int:
        return max(2, int(self.stopped_seconds * self.fps))

    def detect(self, tracks: list[Track]) -> list[Incident]:
        incidents: list[Incident] = []
        incidents.extend(self._stopped(tracks))
        incidents.extend(self._wrong_way(tracks))
        incidents.extend(self._lane_changes(tracks))
        return incidents

    def _stopped(self, tracks: list[Track]) -> list[Incident]:
        window = self._stopped_window()
        out: list[Incident] = []
        for track in tracks:
            if len(track.history) < window:
                continue
            recent = track.history[-window:]
            xs = [cx for _, cx, _ in recent]
            ys = [cy for _, _, cy in recent]
            travel = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5
            if travel <= self.stopped_pixel_eps:
                out.append(
                    Incident(IncidentKind.STOPPED_VEHICLE, track.track_id, track.label, 0.85)
                )
        return out

    def _wrong_way(self, tracks: list[Track]) -> list[Incident]:
        moving = [t for t in tracks if abs(t.vx) >= 0.2]
        if len(moving) < 2:
            return []
        flow = median(t.vx for t in moving)
        if abs(flow) < 0.3:
            return []
        out: list[Incident] = []
        for track in moving:
            opposes = (track.vx * flow) < 0
            if opposes and abs(track.vx) >= self.wrong_way_min_speed:
                out.append(
                    Incident(IncidentKind.WRONG_WAY, track.track_id, track.label, 0.8)
                )
        return out

    def _lane_changes(self, tracks: list[Track]) -> list[Incident]:
        out: list[Incident] = []
        for track in tracks:
            if len(track.history) < self.lane_change_window:
                continue
            recent = track.history[-self.lane_change_window :]
            dy = abs(recent[-1][2] - recent[0][2])
            if track.h > 0 and dy >= self.lane_change_ratio * track.h:
                out.append(
                    Incident(IncidentKind.SUDDEN_LANE_CHANGE, track.track_id, track.label, 0.6)
                )
        return out
