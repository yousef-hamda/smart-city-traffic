"""Application entrypoint: ``uvicorn federated_coordinator.main:app``."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from federated_coordinator import __version__
from federated_coordinator.config import settings
from federated_coordinator.logging import configure_logging
from federated_coordinator.telemetry import setup_telemetry

logger = structlog.get_logger()


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("service_started", port=settings.port, version=__version__)
    yield
    logger.info("service_stopped")


def create_app() -> FastAPI:
    """Build the FastAPI app; kept as a factory for tests."""
    app = FastAPI(title="Federated Learning Coordinator", version=__version__, lifespan=_lifespan)
    setup_telemetry(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name, "version": __version__}

    return app


app = create_app()
