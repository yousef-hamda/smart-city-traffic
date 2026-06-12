"""Per-camera processing: detect → track → detect incidents → aggregate.

One :class:`CameraPipeline` per camera holds that camera's tracker so identities
persist across frames. The pipeline is pure (no Kafka, no Redis) and fully
unit-testable; the consumer wires it to I/O.
"""

import base64
import time
from dataclasses import dataclass, field

import numpy as np

from vision_service.detection import Detector
from vision_service.incidents import Incident, IncidentDetector
from vision_service.tracking import ByteTracker, Track


@dataclass
class VisionEvent:
    """Enriched per-frame result published to ``vision.events``."""

    camera_id: str
    segment_id: str
    seq: int
    ts: str
    vehicle_counts: dict[str, int]
    total_vehicles: int
    avg_dwell_s: float
    incidents: list[Incident]
    tracks: list[Track]

    def to_envelope(self) -> dict[str, object]:
        return {
            "camera_id": self.camera_id,
            "segment_id": self.segment_id,
            "seq": self.seq,
            "ts": self.ts,
            "vehicle_counts": self.vehicle_counts,
            "total_vehicles": self.total_vehicles,
            "avg_dwell_s": round(self.avg_dwell_s, 2),
            "incidents": [
                {
                    "kind": i.kind.value,
                    "track_id": i.track_id,
                    "label": i.label,
                    "confidence": i.confidence,
                }
                for i in self.incidents
            ],
            "tracks": [
                {
                    "id": t.track_id,
                    "label": t.label,
                    "bbox": [round(v, 1) for v in t.xyxy],
                }
                for t in self.tracks
            ],
        }


def decode_frame(image_b64: str) -> np.ndarray:
    """Decode a base64 JPEG envelope field into a BGR frame."""
    import cv2

    raw = base64.b64decode(image_b64)
    buffer = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("could not decode frame JPEG")
    return frame


@dataclass
class CameraPipeline:
    camera_id: str
    segment_id: str
    detector: Detector
    incident_detector: IncidentDetector
    fps: float
    tracker: ByteTracker = field(default_factory=ByteTracker)

    def process(self, frame: np.ndarray, seq: int, ts: str) -> VisionEvent:
        detections = self.detector.detect(frame)
        tracks = self.tracker.step(detections)

        counts: dict[str, int] = {}
        for track in tracks:
            counts[track.label] = counts.get(track.label, 0) + 1

        dwell = (
            sum(track.age for track in tracks) / len(tracks) / self.fps if tracks else 0.0
        )
        incidents = self.incident_detector.detect(tracks)

        return VisionEvent(
            camera_id=self.camera_id,
            segment_id=self.segment_id,
            seq=seq,
            ts=ts,
            vehicle_counts=counts,
            total_vehicles=len(tracks),
            avg_dwell_s=dwell,
            incidents=incidents,
            tracks=tracks,
        )


def annotate(frame: np.ndarray, event: VisionEvent) -> np.ndarray:
    """Draw track boxes, ids, and incident flags onto a copy of the frame."""
    import cv2

    canvas = frame.copy()
    incident_ids = {i.track_id for i in event.incidents}
    for track in event.tracks:
        x1, y1, x2, y2 = (int(v) for v in track.xyxy)
        color = (0, 0, 230) if track.track_id in incident_ids else (60, 220, 60)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            canvas,
            f"#{track.track_id} {track.label}",
            (x1, max(12, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )
    for offset, incident in enumerate(event.incidents):
        cv2.putText(
            canvas,
            f"! {incident.kind.value} #{incident.track_id}",
            (16, 70 + offset * 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 230),
            2,
            cv2.LINE_AA,
        )
    return canvas


def encode_png(frame: np.ndarray) -> bytes:
    import cv2

    ok, buf = cv2.imencode(".png", frame)
    if not ok:  # pragma: no cover
        raise RuntimeError("PNG encoding failed")
    return buf.tobytes()


def monotonic_ms() -> int:
    return int(time.monotonic() * 1000)
