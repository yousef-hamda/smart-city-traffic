"""Wire format for a published camera frame.

Frames go onto Kafka topic ``vision.frames`` as a JSON envelope with the JPEG
bytes base64-encoded. The vision service decodes the envelope, runs YOLOv8 on
the image, and emits ``vision.events``. Keeping metadata alongside the image
means the consumer never has to guess the camera, sequence, or capture time.
"""

import base64
from dataclasses import dataclass


@dataclass(frozen=True)
class Frame:
    camera_id: str
    segment_id: str
    seq: int
    ts: str
    width: int
    height: int
    jpeg: bytes
    # Ground-truth incident hints (the vision service must still detect these
    # independently; they are included only for evaluation/debugging).
    incident_hints: tuple[str, ...] = ()

    def to_envelope(self) -> dict[str, object]:
        return {
            "camera_id": self.camera_id,
            "segment_id": self.segment_id,
            "seq": self.seq,
            "ts": self.ts,
            "width": self.width,
            "height": self.height,
            "format": "jpeg",
            "image_b64": base64.b64encode(self.jpeg).decode("ascii"),
            "incident_hints": list(self.incident_hints),
        }
