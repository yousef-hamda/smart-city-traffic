"""Application entrypoint: ``uvicorn vision_service.main:app``."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from vision_service import __version__
from vision_service.config import settings
from vision_service.logging import configure_logging
from vision_service.telemetry import setup_telemetry

logger = structlog.get_logger()


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("service_started", port=settings.port, version=__version__)
    yield
    logger.info("service_stopped")


def create_app() -> FastAPI:
    """Build the FastAPI app; kept as a factory for tests."""
    app = FastAPI(title="Vision Service", version=__version__, lifespan=_lifespan)
    setup_telemetry(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name, "version": __version__}

    return app


app = create_app()
