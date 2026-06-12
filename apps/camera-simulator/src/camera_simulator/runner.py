"""Multi-camera frame loop: advance scenes, render, publish at a target FPS."""

import time
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

import structlog

from camera_simulator.frames import Frame
from camera_simulator.publishers import FramePublisher
from camera_simulator.renderer import FRAME_HEIGHT, FRAME_WIDTH, RenderContext, encode_jpeg, render
from camera_simulator.scene import IncidentKind, Scene, SceneConfig

logger = structlog.get_logger()

JERUSALEM_TZ = ZoneInfo("Asia/Jerusalem")


@dataclass
class CameraSpec:
    camera_id: str
    segment_id: str
    config: SceneConfig


@dataclass
class Camera:
    spec: CameraSpec
    scene: Scene = field(init=False)
    seq: int = 0

    def __post_init__(self) -> None:
        self.scene = Scene(self.spec.config)

    def next_frame(self, jpeg_quality: int) -> Frame:
        self.scene.step()
        self.seq += 1
        ctx = RenderContext(
            camera_id=self.spec.camera_id,
            timestamp_iso=datetime.now(tz=JERUSALEM_TZ).isoformat(timespec="seconds"),
        )
        image = render(self.scene, ctx)
        hints = tuple(kind.value for kind in self.scene.active_incidents.values())
        return Frame(
            camera_id=self.spec.camera_id,
            segment_id=self.spec.segment_id,
            seq=self.seq,
            ts=ctx.timestamp_iso,
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT,
            jpeg=encode_jpeg(image, jpeg_quality),
            incident_hints=hints,
        )


@dataclass
class CameraRunner:
    cameras: list[Camera]
    publisher: FramePublisher
    fps: int
    jpeg_quality: int = 80

    def run(self, duration_s: float | None = None, max_frames: int | None = None) -> int:
        """Loop until duration/frame budget hits or interrupted; returns frames sent."""
        interval = 1.0 / self.fps
        produced = 0
        started = time.monotonic()
        logger.info("camera_sim_started", cameras=len(self.cameras), fps=self.fps)
        try:
            while True:
                tick = time.monotonic()
                for camera in self.cameras:
                    self.publisher.publish(camera.next_frame(self.jpeg_quality))
                    produced += 1
                if max_frames is not None and produced >= max_frames:
                    break
                if duration_s is not None and time.monotonic() - started >= duration_s:
                    break
                time.sleep(max(0.0, interval - (time.monotonic() - tick)))
        except KeyboardInterrupt:  # pragma: no cover - interactive only
            logger.info("camera_sim_interrupted")
        logger.info("camera_sim_finished", frames=produced)
        return produced

    def inject(self, camera_id: str, kind: IncidentKind) -> None:
        for camera in self.cameras:
            if camera.spec.camera_id == camera_id:
                camera.scene.inject_incident(kind)
                logger.info("incident_injected", camera_id=camera_id, kind=kind.value)
                return
        raise KeyError(camera_id)
