"""Application entrypoint: ``uvicorn vision_service.main:app``."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

from vision_service import __version__
from vision_service.config import settings
from vision_service.consumer import VisionConsumer
from vision_service.logging import configure_logging
from vision_service.snapshots import SnapshotStore
from vision_service.telemetry import setup_telemetry

logger = structlog.get_logger()


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    store: SnapshotStore = app.state.snapshots
    consumer = VisionConsumer(settings, store)
    app.state.consumer = consumer
    consumer.start()
    logger.info(
        "service_started",
        port=settings.port,
        version=__version__,
        detector=settings.detector,
    )
    yield
    consumer.stop()
    logger.info("service_stopped")


def create_app() -> FastAPI:
    """Build the FastAPI app; kept as a factory for tests."""
    app = FastAPI(title="Vision Service", version=__version__, lifespan=_lifespan)
    app.state.snapshots = SnapshotStore()
    setup_telemetry(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name, "version": __version__}

    @app.get("/snapshot/{segment_id}")
    async def snapshot(segment_id: str) -> Response:
        """Return the latest annotated frame for a segment as a PNG."""
        png = app.state.snapshots.get(segment_id)
        if png is None:
            return JSONResponse(
                status_code=404,
                content={"detail": f"no snapshot yet for segment {segment_id}"},
            )
        return Response(content=png, media_type="image/png")

    @app.get("/segments")
    async def segments() -> dict[str, list[str]]:
        """List segments that currently have a snapshot available."""
        return {"segments": app.state.snapshots.segments()}

    return app


app = create_app()
