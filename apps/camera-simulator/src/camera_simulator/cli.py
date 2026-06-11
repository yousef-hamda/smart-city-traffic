"""Command-line interface for the camera simulator.

Phase 1 skeleton: argument surface and logging are real, frame synthesis
(OpenCV sprites, RTSP server, Kafka publishing) lands in Phase 3.
"""

import click
import structlog

from camera_simulator.logging import configure_logging

logger = structlog.get_logger()


@click.group()
def cli() -> None:
    """Synthetic traffic camera simulator."""
    configure_logging()


@cli.command()
@click.option("--fps", type=click.IntRange(min=1, max=30), default=15, show_default=True,
              help="Frames per second per camera.")
@click.option("--cameras", type=click.IntRange(min=1), default=4, show_default=True,
              help="Number of simulated cameras.")
def run(fps: int, cameras: int) -> None:
    """Render synthetic frames and publish to RTSP / Kafka."""
    logger.info("camera_simulator_skeleton", mode="run", fps=fps, cameras=cameras,
                note="frame synthesis lands in Phase 3")
