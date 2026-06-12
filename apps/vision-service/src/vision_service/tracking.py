"""ByteTrack-style multi-object tracker.

ByteTrack's core insight: don't throw away low-confidence detections. Most
trackers keep only high-score boxes and lose objects the moment they are
partially occluded (and their score dips). ByteTrack runs association in two
stages — high-score detections first, then the *leftover low-score* boxes
against still-unmatched tracks — which recovers those fading objects and
markedly reduces ID switches.

This implementation keeps that two-stage strategy and a constant-velocity
motion model, but uses greedy IoU association rather than the Hungarian
algorithm to stay dependency-free (numpy only). For the densities in this
simulation the two produce near-identical assignments; the Hungarian solver is
the drop-in upgrade if ID-switch rate ever needs tightening.

State machine per track: ``tentative`` → ``confirmed`` (after
``min_hits`` consecutive matches) → ``lost`` (unmatched) → removed (lost for
``max_age`` frames). IDs are stable across the ``lost`` window so a brief
occlusion does not mint a new identity.
"""

from dataclasses import dataclass, field
from enum import StrEnum

from vision_service.detection import Detection


class TrackState(StrEnum):
    TENTATIVE = "tentative"
    CONFIRMED = "confirmed"
    LOST = "lost"


def iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    """Intersection-over-union of two ``(x1, y1, x2, y2)`` boxes."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


@dataclass
class Track:
    """A single tracked object with a constant-velocity center estimate."""

    track_id: int
    label: str
    cx: float
    cy: float
    w: float
    h: float
    vx: float = 0.0
    vy: float = 0.0
    state: TrackState = TrackState.TENTATIVE
    hits: int = 1
    age: int = 0
    time_since_update: int = 0
    # Center history (frame_index, cx, cy) for incident heuristics.
    history: list[tuple[int, float, float]] = field(default_factory=list)

    @property
    def xyxy(self) -> tuple[float, float, float, float]:
        return (
            self.cx - self.w / 2,
            self.cy - self.h / 2,
            self.cx + self.w / 2,
            self.cy + self.h / 2,
        )

    def predict(self) -> None:
        """Advance the center by its velocity (called once per frame)."""
        self.cx += self.vx
        self.cy += self.vy
        self.age += 1
        self.time_since_update += 1

    def update(self, detection: Detection, frame_index: int, smoothing: float = 0.5) -> None:
        """Correct the state toward a matched detection."""
        ncx, ncy = detection.center
        new_vx, new_vy = ncx - self.cx, ncy - self.cy
        # EMA-smooth the velocity so a single noisy frame doesn't whip the track.
        self.vx = smoothing * new_vx + (1 - smoothing) * self.vx
        self.vy = smoothing * new_vy + (1 - smoothing) * self.vy
        self.cx, self.cy = ncx, ncy
        self.w, self.h = detection.w, detection.h
        self.hits += 1
        self.time_since_update = 0
        self.history.append((frame_index, self.cx, self.cy))


@dataclass
class ByteTrackConfig:
    high_thresh: float = 0.5
    low_thresh: float = 0.1
    match_iou: float = 0.3
    min_hits: int = 3
    max_age: int = 30
    history_limit: int = 600


class ByteTracker:
    """Two-stage IoU tracker over a stream of per-frame detections."""

    def __init__(self, config: ByteTrackConfig | None = None) -> None:
        self.config = config or ByteTrackConfig()
        self._tracks: list[Track] = []
        self._next_id = 1
        self._frame_index = 0

    @property
    def tracks(self) -> list[Track]:
        """Currently confirmed (non-lost) tracks."""
        return [t for t in self._tracks if t.state is TrackState.CONFIRMED]

    @property
    def all_tracks(self) -> list[Track]:
        return list(self._tracks)

    def _associate(
        self, tracks: list[Track], detections: list[Detection]
    ) -> tuple[list[tuple[Track, Detection]], list[Track], list[Detection]]:
        """Greedy IoU matching, highest-overlap pair first."""
        pairs: list[tuple[float, Track, Detection]] = []
        for track in tracks:
            for detection in detections:
                score = iou(track.xyxy, detection.xyxy)
                if score >= self.config.match_iou:
                    pairs.append((score, track, detection))
        pairs.sort(key=lambda p: p[0], reverse=True)

        matched: list[tuple[Track, Detection]] = []
        used_tracks: set[int] = set()
        used_dets: set[int] = set()
        for _, track, detection in pairs:
            if id(track) in used_tracks or id(detection) in used_dets:
                continue
            matched.append((track, detection))
            used_tracks.add(id(track))
            used_dets.add(id(detection))

        unmatched_tracks = [t for t in tracks if id(t) not in used_tracks]
        unmatched_dets = [d for d in detections if id(d) not in used_dets]
        return matched, unmatched_tracks, unmatched_dets

    def step(self, detections: list[Detection]) -> list[Track]:
        """Process one frame of detections; returns confirmed tracks."""
        self._frame_index += 1
        for track in self._tracks:
            track.predict()

        high = [d for d in detections if d.confidence >= self.config.high_thresh]
        low = [
            d
            for d in detections
            if self.config.low_thresh <= d.confidence < self.config.high_thresh
        ]

        # Stage 1: all active tracks against high-confidence detections.
        active = [t for t in self._tracks if t.state is not TrackState.LOST] + [
            t for t in self._tracks if t.state is TrackState.LOST
        ]
        matched, unmatched_tracks, unmatched_high = self._associate(active, high)

        # Stage 2: still-unmatched tracks against the low-confidence leftovers.
        matched_low, unmatched_tracks, _ = self._associate(unmatched_tracks, low)
        matched += matched_low

        for track, detection in matched:
            track.update(detection, self._frame_index)
            if (
                track.state is TrackState.TENTATIVE
                and track.hits >= self.config.min_hits
            ) or track.state is TrackState.LOST:
                track.state = TrackState.CONFIRMED

        for track in unmatched_tracks:
            track.state = TrackState.LOST

        # Birth new tracks from unmatched high-confidence detections only.
        for detection in unmatched_high:
            track = Track(
                track_id=self._next_id,
                label=detection.label,
                cx=detection.center[0],
                cy=detection.center[1],
                w=detection.w,
                h=detection.h,
            )
            track.history.append((self._frame_index, track.cx, track.cy))
            self._tracks.append(track)
            self._next_id += 1

        # Reap tracks lost beyond the buffer; trim history.
        self._tracks = [
            t for t in self._tracks if t.time_since_update <= self.config.max_age
        ]
        for track in self._tracks:
            if len(track.history) > self.config.history_limit:
                track.history = track.history[-self.config.history_limit :]

        return self.tracks
