"""Synthetic frame builders shared across tests.

Sprite colors match ``camera_simulator.scene.VEHICLE_COLORS`` so the synthetic
detector finds them — kept in sync by the cross-service contract, not imported
across app boundaries.
"""

import numpy as np

CAR_BGR = (210, 180, 90)
TRUCK_BGR = (90, 120, 220)


def make_frame(boxes: list[tuple[int, int, int, int, tuple[int, int, int]]]) -> np.ndarray:
    """Build a 720p frame with filled colored rectangles (x, y, w, h, bgr)."""
    import cv2

    frame = np.full((720, 1280, 3), 30, dtype=np.uint8)
    cv2.rectangle(frame, (0, 140), (1280, 660), (45, 45, 48), -1)
    for x, y, w, h, bgr in boxes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), bgr, -1)
    return frame
