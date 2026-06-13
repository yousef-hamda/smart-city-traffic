"""Application entrypoint: ``uvicorn federated_coordinator.main:app``."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from pydantic import BaseModel, Field

from federated_coordinator import __version__
from federated_coordinator.config import settings
from federated_coordinator.federated import comparison_report
from federated_coordinator.logging import configure_logging
from federated_coordinator.telemetry import setup_telemetry

logger = structlog.get_logger()


class TrainRequest(BaseModel):
    rounds: int = Field(default=25, ge=1, le=200)
    local_epochs: int = Field(default=3, ge=1, le=50)
    secure_aggregation: bool = True


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    app.state.last_report = None
    logger.info("service_started", port=settings.port, version=__version__)
    yield
    logger.info("service_stopped")


def create_app() -> FastAPI:
    """Build the FastAPI app; kept as a factory for tests."""
    app = FastAPI(title="Federated Learning Coordinator", version=__version__, lifespan=_lifespan)
    app.state.last_report = None
    setup_telemetry(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name, "version": __version__}

    @app.post("/train/federated")
    async def train_federated(req: TrainRequest) -> dict[str, object]:
        """Run a federated training session and return the comparison report."""
        report = comparison_report(
            rounds=req.rounds,
            local_epochs=req.local_epochs,
            secure=req.secure_aggregation,
        )
        app.state.last_report = report
        logger.info(
            "federated_round_complete",
            federated_mse=report["federated_mse"],
            centralized_mse=report["centralized_mse"],
        )
        return report

    @app.get("/report")
    async def last_report() -> dict[str, object]:
        """Return the most recent comparison report (or a 'not run' marker)."""
        if app.state.last_report is None:
            return {"status": "no_run_yet"}
        return app.state.last_report  # type: ignore[no-any-return]

    return app


app = create_app()
