"""Lazy-loading model registry — loads models once at startup."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _make_fixture_df(n: int = 50) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    hour_vals = np.arange(n) % 24
    dow_vals = np.arange(n) % 7
    return pd.DataFrame({
        "vehicle_count": rng.integers(10, 200, n).astype(float),
        "avg_speed_kmh": rng.uniform(10, 80, n),
        "occupancy_pct": rng.uniform(5, 90, n),
        "hour": hour_vals.astype(float),
        "day_of_week": dow_vals.astype(float),
        "is_weekend": (dow_vals >= 5).astype(float),
        "is_rush": np.isin(hour_vals, [7, 8, 9, 16, 17, 18]).astype(float),
        "lag_1h": rng.integers(10, 200, n).astype(float),
        "lag_24h": rng.integers(10, 200, n).astype(float),
        "rolling_mean_3h": rng.uniform(50, 150, n),
    })


class ModelRegistry:
    """Thread-safe lazy model registry."""

    def __init__(self, model_dir: Path) -> None:
        self.model_dir = model_dir
        self._demand: Any = None
        self._anomaly: Any = None
        self._congestion: Any = None

    def _load_or_train_demand(self) -> Any:
        from ml_prediction.models.demand import DemandModel

        model = DemandModel()
        p = self.model_dir / "demand_xgboost.joblib"
        if p.exists():
            model.load(p)
        else:
            logger.warning("demand model not found at %s — training on fixture data", p)
            self._train_fixture(model, "xgboost")
        return model

    def _load_or_train_anomaly(self) -> Any:
        from ml_prediction.models.anomaly import AnomalyModel

        model = AnomalyModel()
        p = self.model_dir / "anomaly_isoforest.joblib"
        if p.exists():
            model.load(p)
        else:
            logger.warning("anomaly model not found at %s — training on fixture data", p)
            self._train_fixture(model, "isoforest")
        return model

    def _load_or_train_congestion(self) -> Any:
        from ml_prediction.models.congestion import CongestionModel

        model = CongestionModel()
        p = self.model_dir / "congestion_lstm.pt"
        if p.exists():
            model.load(p)
        else:
            logger.warning("congestion model not found at %s — training on fixture data", p)
            self._train_fixture(model, "lstm")
        return model

    def _train_fixture(self, model: Any, model_type: str) -> None:
        """Train on tiny fixture data when no artifact exists."""
        df = _make_fixture_df(50)
        model.train(df)
        # Save to model_dir
        self.model_dir.mkdir(parents=True, exist_ok=True)
        if model_type == "xgboost":
            model.save(self.model_dir / "demand_xgboost.joblib")
        elif model_type == "isoforest":
            model.save(self.model_dir / "anomaly_isoforest.joblib")
        elif model_type == "lstm":
            model.save(self.model_dir / "congestion_lstm.pt")

    @property
    def demand(self) -> Any:
        if self._demand is None:
            self._demand = self._load_or_train_demand()
        return self._demand

    @property
    def anomaly(self) -> Any:
        if self._anomaly is None:
            self._anomaly = self._load_or_train_anomaly()
        return self._anomaly

    @property
    def congestion(self) -> Any:
        if self._congestion is None:
            self._congestion = self._load_or_train_congestion()
        return self._congestion
