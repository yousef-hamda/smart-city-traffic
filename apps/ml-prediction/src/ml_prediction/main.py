"""Application entrypoint: ``uvicorn ml_prediction.main:app``."""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC

import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ml_prediction import __version__
from ml_prediction.config import settings
from ml_prediction.logging import configure_logging
from ml_prediction.model_registry import ModelRegistry
from ml_prediction.telemetry import setup_telemetry

logger = structlog.get_logger()
_std_logger = logging.getLogger(__name__)

# Global model registry
_registry: ModelRegistry | None = None


# ---------------------------------------------------------------------------
# Request / Response schemas (Pydantic v2)
# ---------------------------------------------------------------------------


class DemandRequest(BaseModel):
    segment_id: str
    horizon_hours: int = Field(default=6, ge=1, le=24)


class HourlyPrediction(BaseModel):
    hour: int
    vehicle_count: float


class DemandResponse(BaseModel):
    predictions: list[HourlyPrediction]
    model_version: str


class ReadingInput(BaseModel):
    speed: float
    occupancy: float
    count: float


class AnomalyRequest(BaseModel):
    segment_id: str
    readings: list[ReadingInput] | None = None


class AnomalyResponse(BaseModel):
    is_anomaly: bool
    score: float
    model_version: str


class CongestionRequest(BaseModel):
    segment_id: str
    horizon_minutes: int = Field(default=30, ge=15, le=60)


class ShapItem(BaseModel):
    feature: str
    value: float


class CongestionResponse(BaseModel):
    predicted_speed_kmh: float
    lower_ci: float
    upper_ci: float
    shap_top5: list[ShapItem]
    model_version: str


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _registry
    configure_logging()
    logger.info("service_started", port=settings.port, version=__version__)

    _registry = ModelRegistry(model_dir=settings.model_dir)
    # Eagerly load models to warm up
    try:
        _ = _registry.demand
        _ = _registry.anomaly
        _ = _registry.congestion
        logger.info("models_loaded")
    except Exception as exc:
        _std_logger.warning("Model warm-up failed: %s", exc)

    # Start gRPC server in background
    try:
        from ml_prediction.grpc_server import start_grpc_server

        start_grpc_server(_registry, port=settings.grpc_port)
        logger.info("grpc_server_started", port=settings.grpc_port)
    except Exception as exc:
        _std_logger.warning("gRPC server failed to start: %s", exc)

    yield

    # Shutdown
    try:
        from ml_prediction.grpc_server import stop_grpc_server

        stop_grpc_server()
    except Exception:
        pass
    logger.info("service_stopped")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Build the FastAPI app; kept as a factory for tests."""
    app = FastAPI(title="ML Prediction Service", version=__version__, lifespan=_lifespan)
    setup_telemetry(app)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.service_name, "version": __version__}

    @app.post("/forecast/demand", response_model=DemandResponse)
    async def forecast_demand(req: DemandRequest) -> DemandResponse:
        if _registry is None:
            raise HTTPException(status_code=503, detail="Model registry not initialised")
        from datetime import datetime, timedelta

        import numpy as np
        import pandas as pd

        model = _registry.demand
        now = datetime.now(UTC)
        predictions: list[HourlyPrediction] = []
        rng = np.random.default_rng(42)

        for h in range(1, req.horizon_hours + 1):
            hour_dt = now + timedelta(hours=h)
            X = pd.DataFrame({
                "hour": [hour_dt.hour],
                "day_of_week": [hour_dt.weekday()],
                "is_weekend": [1 if hour_dt.weekday() >= 5 else 0],
                "is_rush": [1 if hour_dt.hour in [7, 8, 9, 16, 17, 18] else 0],
                "lag_1h": [float(rng.integers(50, 150))],
                "lag_24h": [float(rng.integers(50, 150))],
                "rolling_mean_3h": [float(rng.uniform(60, 130))],
            })
            pred = model.predict(X)
            predictions.append(HourlyPrediction(hour=h, vehicle_count=float(max(0, pred[0]))))

        return DemandResponse(predictions=predictions, model_version=model.model_version)

    @app.post("/detect/anomaly", response_model=AnomalyResponse)
    async def detect_anomaly(req: AnomalyRequest) -> AnomalyResponse:
        if _registry is None:
            raise HTTPException(status_code=503, detail="Model registry not initialised")

        model = _registry.anomaly

        if req.readings:
            # Average the readings for anomaly detection
            speed = sum(r.speed for r in req.readings) / len(req.readings)
            occupancy = sum(r.occupancy for r in req.readings) / len(req.readings)
            count = sum(r.count for r in req.readings) / len(req.readings)
        else:
            import numpy as np

            rng = np.random.default_rng(42)
            speed = float(rng.uniform(20, 60))
            occupancy = float(rng.uniform(10, 70))
            count = float(rng.integers(50, 150))

        result = model.detect(
            {"avg_speed_kmh": speed, "occupancy_pct": occupancy, "vehicle_count": count}
        )
        return AnomalyResponse(
            is_anomaly=bool(result["is_anomaly"]),
            score=float(result["score"]),
            model_version=model.model_version,
        )

    @app.post("/predict/congestion", response_model=CongestionResponse)
    async def predict_congestion(req: CongestionRequest) -> CongestionResponse:
        if _registry is None:
            raise HTTPException(status_code=503, detail="Model registry not initialised")

        import numpy as np
        import pandas as pd

        from ml_prediction.explain import get_top5_shap
        from ml_prediction.models.demand import FEATURES

        model = _registry.congestion
        rng = np.random.default_rng(42)
        n = 10
        recent_df = pd.DataFrame({
            "vehicle_count": rng.integers(50, 150, n).astype(float),
            "avg_speed_kmh": rng.uniform(20, 70, n),
            "occupancy_pct": rng.uniform(10, 70, n),
            "hour": np.full(n, 8.0),
            "is_rush": np.ones(n),
        })
        result = model.predict_speed(recent_df)

        X_shap = pd.DataFrame({f: [0.0] for f in FEATURES})
        raw_shap = get_top5_shap(
            model._net if hasattr(model, "_net") else model,
            X_shap,
            model_type="lstm",
            feature_names=FEATURES,
        )
        shap_top5 = [ShapItem(feature=c["feature"], value=c["value"]) for c in raw_shap]

        return CongestionResponse(
            predicted_speed_kmh=result["mean"],
            lower_ci=result["lower"],
            upper_ci=result["upper"],
            shap_top5=shap_top5,
            model_version=model.model_version,
        )

    return app


app = create_app()
