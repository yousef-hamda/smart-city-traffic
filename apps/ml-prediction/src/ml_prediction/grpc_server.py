"""gRPC server implementing PredictionService on port 9093.

Started in a background thread from the FastAPI lifespan hook.
Generated proto stubs live under src/ml_prediction/proto/.
"""
from __future__ import annotations

import logging
import sys
import threading
import time
from concurrent import futures
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import grpc

# Ensure proto stubs are importable
_PROTO_DIR = Path(__file__).resolve().parent / "proto"
if str(_PROTO_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTO_DIR))

logger = logging.getLogger(__name__)

_server: grpc.Server | None = None
_thread: threading.Thread | None = None


def _get_timestamp() -> Any:
    """Return a protobuf Timestamp for now."""
    from google.protobuf.timestamp_pb2 import Timestamp

    ts = Timestamp()
    ts.FromDatetime(datetime.now(UTC))
    return ts


class PredictionServicer:
    """gRPC service implementation delegating to model_registry."""

    def __init__(self, registry: Any) -> None:
        self.registry = registry

    def Predict(self, request: Any, context: Any) -> Any:
        """Congestion speed prediction."""
        try:
            import numpy as np
            import pandas as pd

            from ml_prediction.explain import get_top5_shap
            from ml_prediction.models.demand import FEATURES
            from ml_prediction.proto.traffic.v1 import (
                prediction_pb2,
            )

            model = self.registry.congestion
            # Build a minimal recent_df from fixture data
            n = 10
            rng = np.random.default_rng(42)
            recent_df = pd.DataFrame({
                "vehicle_count": rng.integers(50, 150, n).astype(float),
                "avg_speed_kmh": rng.uniform(20, 70, n),
                "occupancy_pct": rng.uniform(10, 70, n),
                "hour": np.full(n, datetime.now().hour, dtype=float),
                "is_rush": np.zeros(n),
            })
            result = model.predict_speed(recent_df)
            mean_speed = result["mean"]
            lower = result["lower"]
            upper = result["upper"]

            # Build dummy X for SHAP
            X_shap = pd.DataFrame({f: [0.0] for f in FEATURES})
            shap_contributions = get_top5_shap(
                model._net if hasattr(model, "_net") else model,
                X_shap,
                model_type="lstm",
                feature_names=FEATURES,
            )

            response = prediction_pb2.PredictResponse(
                segment_id=request.segment_id,
                horizon_minutes=request.horizon_minutes,
                predicted_speed_kmh=mean_speed,
                lower_ci=lower,
                upper_ci=upper,
                model_version=model.model_version,
                generated_at=_get_timestamp(),
            )
            for c in shap_contributions:
                response.shap_top5.add(feature=c["feature"], value=c["value"])
            return response
        except Exception as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            raise

    def DetectAnomaly(self, request: Any, context: Any) -> Any:
        """Anomaly detection."""
        try:
            import numpy as np

            from ml_prediction.proto.traffic.v1 import (
                prediction_pb2,
            )

            model = self.registry.anomaly
            rng = np.random.default_rng(42)
            reading = {
                "avg_speed_kmh": float(rng.uniform(20, 60)),
                "occupancy_pct": float(rng.uniform(10, 70)),
                "vehicle_count": float(rng.integers(50, 150)),
            }
            result = model.detect(reading)
            return prediction_pb2.AnomalyResponse(
                segment_id=request.segment_id,
                is_anomaly=result["is_anomaly"],
                score=result["score"],
                model_version=model.model_version,
            )
        except Exception as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            raise

    def ForecastDemand(self, request: Any, context: Any) -> Any:
        """Demand forecasting."""
        try:
            from datetime import timedelta

            import numpy as np
            import pandas as pd

            from ml_prediction.proto.traffic.v1 import (
                prediction_pb2,
            )

            model = self.registry.demand
            now = datetime.now(UTC)
            hourly = []
            rng = np.random.default_rng(42)

            for h in range(1, min(request.horizon_hours + 1, 25)):
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
                count = max(0, int(pred[0]))

                from google.protobuf.timestamp_pb2 import Timestamp

                ts2 = Timestamp()
                ts2.FromDatetime(hour_dt)
                hourly.append(
                    prediction_pb2.HourlyDemand(hour=ts2, predicted_vehicle_count=count)
                )

            return prediction_pb2.DemandResponse(
                segment_id=request.segment_id,
                hourly=hourly,
                model_version=model.model_version,
            )
        except Exception as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            raise


def start_grpc_server(registry: Any, port: int = 9093) -> None:
    """Start gRPC server in background thread."""
    global _server, _thread

    def _run() -> None:
        global _server
        try:
            # Import generated servicer base
            from ml_prediction.proto.traffic.v1 import (
                prediction_pb2_grpc,
            )

            _server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
            servicer = PredictionServicer(registry)
            prediction_pb2_grpc.add_PredictionServiceServicer_to_server(servicer, _server)
            _server.add_insecure_port(f"[::]:{port}")
            _server.start()
            logger.info("gRPC server started on port %d", port)
            _server.wait_for_termination()
        except Exception as exc:
            logger.error("gRPC server error: %s", exc)

    _thread = threading.Thread(target=_run, daemon=True, name="grpc-server")
    _thread.start()
    # Give it a moment to start
    time.sleep(0.1)


def stop_grpc_server() -> None:
    """Graceful gRPC shutdown."""
    global _server
    if _server is not None:
        _server.stop(grace=2.0)
        _server = None
        logger.info("gRPC server stopped")
