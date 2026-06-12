"""Command-line interface for the camera simulator.

Examples:
    python -m camera_simulator run --fps 15 --cameras 4 --output file --out-dir ./frames
    python -m camera_simulator run --output kafka --kafka localhost:29092
    python -m camera_simulator run --output rtsp --rtsp-url rtsp://localhost:8554/cam
"""

from pathlib import Path

import click
import structlog

from camera_simulator.cameras import derive_cameras
from camera_simulator.logging import configure_logging
from camera_simulator.publishers import (
    CompositeFramePublisher,
    FileFramePublisher,
    FramePublisher,
    KafkaFramePublisher,
    RtspFramePublisher,
)
from camera_simulator.renderer import FRAME_HEIGHT, FRAME_WIDTH
from camera_simulator.runner import Camera, CameraRunner, CameraSpec
from camera_simulator.scene import IncidentKind, SceneConfig

logger = structlog.get_logger()


def _build_cameras(count: int, density: float, lanes: int, seed: int | None) -> list[Camera]:
    try:
        mapping = derive_cameras()
    except FileNotFoundError:
        mapping = [(f"C-cam-{i:02d}", f"cam-segment-{i:02d}") for i in range(count)]
    if not mapping:
        mapping = [(f"C-cam-{i:02d}", f"cam-segment-{i:02d}") for i in range(count)]

    cameras: list[Camera] = []
    for offset, (camera_id, segment_id) in enumerate(mapping[:count]):
        config = SceneConfig(
            lanes=lanes,
            density=density,
            # Vary the per-camera seed so feeds aren't identical, but stay
            # reproducible when a seed is supplied.
            seed=None if seed is None else seed + offset,
        )
        cameras.append(Camera(CameraSpec(camera_id, segment_id, config)))
    return cameras


def _build_publisher(
    output: str, out_dir: Path, kafka: str | None, rtsp_url: str | None, fps: int
) -> FramePublisher:
    sinks: list[FramePublisher] = []
    if output in ("file", "all"):
        sinks.append(FileFramePublisher(out_dir))
    if output in ("kafka", "all"):
        if not kafka:
            raise click.UsageError("--kafka is required for kafka output")
        sinks.append(KafkaFramePublisher(kafka))
    if output in ("rtsp", "all"):
        if not rtsp_url:
            raise click.UsageError("--rtsp-url is required for rtsp output")
        sinks.append(RtspFramePublisher(rtsp_url, FRAME_WIDTH, FRAME_HEIGHT, fps))
    if not sinks:
        raise click.UsageError(f"unknown output: {output}")
    return CompositeFramePublisher(sinks)


@click.group()
def cli() -> None:
    """Synthetic traffic camera simulator."""
    configure_logging()


@cli.command()
@click.option("--fps", type=click.IntRange(min=1, max=30), default=15, show_default=True)
@click.option("--cameras", "camera_count", type=click.IntRange(min=1), default=4,
              show_default=True, help="Number of simulated cameras.")
@click.option("--lanes", type=click.IntRange(min=1, max=6), default=3, show_default=True)
@click.option("--density", type=click.FloatRange(min=0.0), default=1.0, show_default=True,
              help="0 = empty road, 1 = nominal, >1 = congestion.")
@click.option("--output", type=click.Choice(["file", "kafka", "rtsp", "all"]),
              default="file", show_default=True)
@click.option("--out-dir", type=click.Path(path_type=Path), default=Path("./frames"),
              show_default=True, help="Directory for file output.")
@click.option("--kafka", envvar="KAFKA_BOOTSTRAP_SERVERS", default=None,
              help="Kafka bootstrap servers for vision.frames.")
@click.option("--rtsp-url", default=None, help="RTSP push URL (requires ffmpeg).")
@click.option("--duration", type=float, default=None, help="Stop after N seconds.")
@click.option("--max-frames", type=int, default=None, help="Stop after N total frames.")
@click.option("--jpeg-quality", type=click.IntRange(min=10, max=100), default=80,
              show_default=True)
@click.option("--incident", type=click.Choice([k.value for k in IncidentKind]), default=None,
              help="Inject an incident on the first camera at startup.")
@click.option("--seed", type=int, default=None, help="RNG seed for reproducible scenes.")
def run(
    fps: int,
    camera_count: int,
    lanes: int,
    density: float,
    output: str,
    out_dir: Path,
    kafka: str | None,
    rtsp_url: str | None,
    duration: float | None,
    max_frames: int | None,
    jpeg_quality: int,
    incident: str | None,
    seed: int | None,
) -> None:
    """Render synthetic frames and publish to file / Kafka / RTSP."""
    cameras = _build_cameras(camera_count, density, lanes, seed)
    publisher = _build_publisher(output, out_dir, kafka, rtsp_url, fps)
    runner = CameraRunner(cameras, publisher, fps=fps, jpeg_quality=jpeg_quality)
    if incident is not None and cameras:
        runner.inject(cameras[0].spec.camera_id, IncidentKind(incident))
    try:
        runner.run(duration_s=duration, max_frames=max_frames)
    finally:
        publisher.close()
