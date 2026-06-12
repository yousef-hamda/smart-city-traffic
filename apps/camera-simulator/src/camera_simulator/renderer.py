"""Render a :class:`Scene` snapshot to a 720p BGR frame with OpenCV."""

from dataclasses import dataclass

import cv2
import numpy as np

from camera_simulator.scene import Scene, Vehicle

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

_ROAD_TOP = 140
_ROAD_BOTTOM = FRAME_HEIGHT - 60
_ASPHALT = (45, 45, 48)
_LANE_LINE = (200, 200, 200)
_HUD_BG = (20, 20, 20)
_HUD_FG = (235, 235, 235)
_INCIDENT = (40, 40, 230)


@dataclass(frozen=True)
class RenderContext:
    camera_id: str
    timestamp_iso: str


def _lane_bounds(lane: int, lanes: int) -> tuple[int, int]:
    span = (_ROAD_BOTTOM - _ROAD_TOP) / lanes
    top = int(_ROAD_TOP + lane * span)
    bottom = int(_ROAD_TOP + (lane + 1) * span)
    return top, bottom


def _draw_road(frame: np.ndarray, lanes: int) -> None:
    cv2.rectangle(frame, (0, _ROAD_TOP), (FRAME_WIDTH, _ROAD_BOTTOM), _ASPHALT, -1)
    for lane in range(1, lanes):
        y = int(_ROAD_TOP + (lane / lanes) * (_ROAD_BOTTOM - _ROAD_TOP))
        for x in range(0, FRAME_WIDTH, 60):
            cv2.line(frame, (x, y), (x + 30, y), _LANE_LINE, 2)


def _draw_vehicle(frame: np.ndarray, vehicle: Vehicle, lanes: int, incident: bool) -> None:
    top, bottom = _lane_bounds(vehicle.lane, lanes)
    height = max(16, int((bottom - top) * 0.55))
    cy = (top + bottom) // 2
    cx = int(vehicle.position * FRAME_WIDTH)
    half_w = vehicle.length_px // 2
    half_h = height // 2

    cv2.rectangle(
        frame,
        (cx - half_w, cy - half_h),
        (cx + half_w, cy + half_h),
        vehicle.color,
        -1,
    )
    cv2.rectangle(
        frame,
        (cx - half_w, cy - half_h),
        (cx + half_w, cy + half_h),
        (20, 20, 20),
        1,
    )
    if incident:
        cv2.rectangle(
            frame,
            (cx - half_w - 4, cy - half_h - 4),
            (cx + half_w + 4, cy + half_h + 4),
            _INCIDENT,
            2,
        )


def _draw_hud(frame: np.ndarray, ctx: RenderContext, vehicle_count: int) -> None:
    cv2.rectangle(frame, (0, 0), (FRAME_WIDTH, 40), _HUD_BG, -1)
    label = f"{ctx.camera_id}  |  {ctx.timestamp_iso}  |  vehicles: {vehicle_count}"
    cv2.putText(
        frame, label, (16, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.6, _HUD_FG, 1, cv2.LINE_AA
    )
    cv2.putText(
        frame,
        "SIMULATED FEED",
        (FRAME_WIDTH - 230, 27),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (80, 80, 200),
        1,
        cv2.LINE_AA,
    )


def render(scene: Scene, ctx: RenderContext) -> np.ndarray:
    """Produce one ``FRAME_HEIGHT x FRAME_WIDTH x 3`` uint8 BGR frame."""
    frame = np.full((FRAME_HEIGHT, FRAME_WIDTH, 3), 30, dtype=np.uint8)
    _draw_road(frame, scene.config.lanes)
    for vehicle in scene.snapshot():
        _draw_vehicle(
            frame, vehicle, scene.config.lanes, incident=vehicle.id in scene.active_incidents
        )
    _draw_hud(frame, ctx, len(scene.vehicles))
    return frame


def encode_jpeg(frame: np.ndarray, quality: int = 80) -> bytes:
    """JPEG-encode a frame for transport over Kafka / RTSP."""
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:  # pragma: no cover - imencode failure is not reproducible in tests
        raise RuntimeError("JPEG encoding failed")
    return buf.tobytes()
