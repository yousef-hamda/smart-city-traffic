"""XGBoost demand model: predicts next-hour vehicle_count."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

logger = logging.getLogger(__name__)

FEATURES = ["hour", "day_of_week", "is_weekend", "is_rush", "lag_1h", "lag_24h", "rolling_mean_3h"]
TARGET = "vehicle_count"
MODEL_VERSION = "xgboost-demand-v1"


class DemandModel:
    """XGBoost regressor wrapped with save/load helpers."""

    model_version: str = MODEL_VERSION

    def __init__(self, params: dict[str, Any] | None = None) -> None:
        default_params: dict[str, Any] = {
            "n_estimators": 50,
            "max_depth": 4,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "tree_method": "hist",
            "device": "cpu",
            "n_jobs": 1,
        }
        if params:
            default_params.update(params)
        self._model = xgb.XGBRegressor(**default_params)
        self._trained = False

    def train(self, df: pd.DataFrame) -> None:
        available = [c for c in FEATURES if c in df.columns]
        X = df[available].fillna(0.0)
        y = df[TARGET]
        self._model.fit(X, y)
        self._trained = True
        logger.info("DemandModel trained on %d rows, features=%s", len(df), available)

    def predict(self, X: pd.DataFrame) -> np.ndarray[Any, np.dtype[np.float64]]:
        available = [c for c in FEATURES if c in X.columns]
        result: np.ndarray[Any, np.dtype[np.float64]] = self._model.predict(
            X[available].fillna(0.0)
        )
        return result

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)
        logger.info("DemandModel saved to %s", path)

    def load(self, path: Path) -> None:
        self._model = joblib.load(path)
        self._trained = True
        logger.info("DemandModel loaded from %s", path)
