"""Application entrypoint: ``uvicorn rl_optimizer.main:app``."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from pydantic import BaseModel, Field

from rl_optimizer import __version__
from rl_optimizer.config import settings
from rl_optimizer.logging import configure_logging
from rl_optimizer.recommend import (
    ApproachState,
    IntersectionState,
    recommend,
)
from rl_optimizer.telemetry import setup_telemetry

logger = structlog.get_logger()


class ApproachIn(BaseModel):
    name: str
    queue: float = Field(ge=0)
    arrival_rate_vps: float = Field(default=0.15, ge=0)


class IntersectionIn(BaseModel):
    name: str
    approaches: list[ApproachIn]
    phases: list[list[int]]
    current_phase: int = 0


class SignalTimingRequest(BaseModel):
    intersections: list[IntersectionIn]


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

    @app.post("/recommend/signal-timing")
    async def recommend_signal_timing(req: SignalTimingRequest) -> dict[str, object]:
        states = [
            IntersectionState(
                name=i.name,
                approaches=[
                    ApproachState(a.name, a.queue, a.arrival_rate_vps) for a in i.approaches
                ],
                phases=i.phases,
                current_phase=i.current_phase,
            )
            for i in req.intersections
        ]
        return {"recommendations": recommend(states)}

    return app


app = create_app()
