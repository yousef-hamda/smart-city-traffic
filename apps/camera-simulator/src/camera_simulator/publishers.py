"""Frame sinks: Kafka (vision.frames), local files, and RTSP via ffmpeg."""

import json
import subprocess
from pathlib import Path
from types import TracebackType
from typing import Protocol

import structlog

from camera_simulator.frames import Frame

logger = structlog.get_logger()

VISION_FRAMES_TOPIC = "vision.frames"


class FramePublisher(Protocol):
    def publish(self, frame: Frame) -> None: ...

    def close(self) -> None: ...


class FileFramePublisher:
    """Writes JPEG frames to disk — used for tests, debugging, and screenshots."""

    def __init__(self, directory: Path) -> None:
        self._dir = directory
        self._dir.mkdir(parents=True, exist_ok=True)

    def publish(self, frame: Frame) -> None:
        path = self._dir / f"{frame.camera_id}_{frame.seq:06d}.jpg"
        path.write_bytes(frame.jpeg)

    def close(self) -> None:  # pragma: no cover - nothing to release
        return None


class KafkaFramePublisher:
    """Publishes the JSON envelope to ``vision.frames``, keyed by camera id."""

    def __init__(self, bootstrap_servers: str) -> None:
        # Imported lazily so file/preview runs don't require kafka-python.
        from kafka import KafkaProducer  # type: ignore[import-not-found]

        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers.split(","),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8"),
            linger_ms=20,
            compression_type="gzip",
        )

    def publish(self, frame: Frame) -> None:
        self._producer.send(
            VISION_FRAMES_TOPIC, key=frame.camera_id, value=frame.to_envelope()
        )

    def close(self) -> None:
        self._producer.flush()
        self._producer.close()


class RtspFramePublisher:
    """Pushes frames to an RTSP endpoint by piping JPEGs through ffmpeg.

    Requires ``ffmpeg`` on PATH and a reachable RTSP server (e.g. mediamtx).
    This is the "looks like a real camera" path; the Kafka path is what the
    rest of the platform actually consumes.
    """

    def __init__(self, rtsp_url: str, width: int, height: int, fps: int) -> None:
        self._proc = subprocess.Popen(  # noqa: S603 - args are fixed, not user shell
            [
                "ffmpeg", "-loglevel", "error", "-y",
                "-f", "image2pipe", "-vcodec", "mjpeg", "-r", str(fps), "-i", "-",
                "-vcodec", "libx264", "-pix_fmt", "yuv420p",
                "-f", "rtsp", rtsp_url,
            ],
            stdin=subprocess.PIPE,
        )
        logger.info("rtsp_started", url=rtsp_url, width=width, height=height, fps=fps)

    def publish(self, frame: Frame) -> None:
        if self._proc.stdin is None:  # pragma: no cover - defensive
            raise RuntimeError("ffmpeg stdin is not available")
        self._proc.stdin.write(frame.jpeg)

    def close(self) -> None:
        if self._proc.stdin is not None:
            self._proc.stdin.close()
        self._proc.wait(timeout=10)


class CompositeFramePublisher:
    def __init__(self, publishers: list[FramePublisher]) -> None:
        self._publishers = publishers

    def publish(self, frame: Frame) -> None:
        for publisher in self._publishers:
            publisher.publish(frame)

    def close(self) -> None:
        for publisher in self._publishers:
            publisher.close()

    def __enter__(self) -> "CompositeFramePublisher":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
