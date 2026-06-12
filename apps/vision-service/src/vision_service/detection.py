"""Vehicle detection.

Two interchangeable detectors implement the same :class:`Detector` protocol:

- :class:`YoloDetector` runs Ultralytics YOLOv8 — the production path for real
  photographic footage. Loaded lazily so the package imports (and tests run)
  without torch installed.
- :class:`SyntheticDetector` uses classical OpenCV (contour + color) tuned to
  the camera simulator's rendered sprites. COCO-trained YOLO does not reliably
  fire on cartoon rectangles, so the synthetic Kafka feed uses this detector to
  produce meaningful tracks. This is an honest engineering split, not a
  shortcut — the tracking, incident, and aggregation layers downstream are
  identical regardless of which detector feeds them.
"""

from dataclasses import dataclass
from typing import Protocol

import numpy as np

# YOLOv8 COCO class ids we treat as vehicles, mapped to platform labels.
_YOLO_VEHICLE_CLASSES: dict[int, str] = {
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

# BGR sprite colors the synthetic renderer uses, mapped back to labels.
_SYNTHETIC_COLORS: dict[str, tuple[int, int, int]] = {
    "car": (210, 180, 90),
    "motorcycle": (90, 220, 250),
    "truck": (90, 120, 220),
    "bus": (60, 200, 120),
}

_COLOR_TOLERANCE = 40
_MIN_CONTOUR_AREA = 350


@dataclass(frozen=True)
class Detection:
    """An axis-aligned detection in pixel coordinates (top-left x/y, w/h)."""

    x: float
    y: float
    w: float
    h: float
    label: str
    confidence: float

    @property
    def xyxy(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.w / 2, self.y + self.h / 2)

    @property
    def area(self) -> float:
        return self.w * self.h


class Detector(Protocol):
    def detect(self, frame: np.ndarray) -> list[Detection]: ...


class SyntheticDetector:
    """Detects the simulator's flat-colored vehicle sprites via color masks."""

    def __init__(self, color_tolerance: int = _COLOR_TOLERANCE) -> None:
        self._tolerance = color_tolerance

    def detect(self, frame: np.ndarray) -> list[Detection]:
        import cv2

        detections: list[Detection] = []
        for label, bgr in _SYNTHETIC_COLORS.items():
            lower = np.array([max(0, c - self._tolerance) for c in bgr], dtype=np.uint8)
            upper = np.array([min(255, c + self._tolerance) for c in bgr], dtype=np.uint8)
            mask = cv2.inRange(frame, lower, upper)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) < _MIN_CONTOUR_AREA:
                    continue
                x, y, w, h = cv2.boundingRect(contour)
                detections.append(
                    Detection(float(x), float(y), float(w), float(h), label, confidence=0.9)
                )
        return detections


class YoloDetector:
    """Ultralytics YOLOv8 detector for real footage (lazy-loaded weights)."""

    def __init__(self, weights: str = "yolov8n.pt", confidence: float = 0.35) -> None:
        self._weights = weights
        self._confidence = confidence
        self._model: object | None = None

    def _ensure_model(self) -> object:
        if self._model is None:
            from ultralytics import YOLO  # type: ignore[import-not-found]

            self._model = YOLO(self._weights)
        return self._model

    def detect(self, frame: np.ndarray) -> list[Detection]:
        model = self._ensure_model()
        results = model.predict(frame, conf=self._confidence, verbose=False)  # type: ignore[attr-defined]
        detections: list[Detection] = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = _YOLO_VEHICLE_CLASSES.get(class_id)
                if label is None:
                    continue
                x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
                detections.append(
                    Detection(
                        x1, y1, x2 - x1, y2 - y1, label, confidence=float(box.conf[0])
                    )
                )
        return detections


def build_detector(kind: str, weights: str, confidence: float) -> Detector:
    if kind == "yolo":
        return YoloDetector(weights, confidence)
    if kind == "synthetic":
        return SyntheticDetector()
    raise ValueError(f"unknown detector: {kind!r}")
