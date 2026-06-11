"""Application entrypoint: ``uvicorn rl_optimizer.main:app``."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from rl_optimizer import __version__
from rl_optimizer.config import settings
from rl_optimizer.logging import configure_logging
from rl_optimizer.telemetry import setup_telemetry

logger = structlog.get_logger()


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    logger.info("service_started", port=settings.port, version=__version__)
    yield
    logger.info("service_stopped")


def create_app() -> FastAPI:
    """Build the FastAPI app; kept as a factory for tests."""
    app = FastAPI(title="RL Signal Optimizer", version=__version__, lifespan=_lifespan)
    setup_telemetry(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name, "version": __version__}

    return app


app = create_app()
