"""Isolation Forest anomaly detection over traffic readings."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

FEATURES = ["avg_speed_kmh", "occupancy_pct", "vehicle_count"]
MODEL_VERSION = "isoforest-anomaly-v1"


class AnomalyModel:
    """IsolationForest wrapper returning is_anomaly + score."""

    model_version: str = MODEL_VERSION

    def __init__(self, contamination: float = 0.05, n_estimators: int = 50) -> None:
        self._model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=42,
            n_jobs=1,
        )
        self._trained = False

    def train(self, df: pd.DataFrame) -> None:
        available = [c for c in FEATURES if c in df.columns]
        X = df[available].fillna(0.0)
        self._model.fit(X)
        self._trained = True
        logger.info("AnomalyModel trained on %d rows", len(df))

    def predict(self, X: pd.DataFrame) -> np.ndarray[Any, np.dtype[np.float64]]:
        available = [c for c in FEATURES if c in X.columns]
        scores: np.ndarray[Any, np.dtype[np.float64]] = self._model.score_samples(
            X[available].fillna(0.0)
        )
        return scores

    def detect(self, reading: dict[str, float]) -> dict[str, Any]:
        """Return is_anomaly + score for a single reading dict."""
        df = pd.DataFrame([reading])
        available = [c for c in FEATURES if c in df.columns]
        X = df[available].fillna(0.0)
        pred: int = int(self._model.predict(X)[0])
        score: float = float(self._model.score_samples(X)[0])
        return {
            "is_anomaly": pred == -1,
            "score": score,
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._model, path)
        logger.info("AnomalyModel saved to %s", path)

    def load(self, path: Path) -> None:
        self._model = joblib.load(path)
        self._trained = True
        logger.info("AnomalyModel loaded from %s", path)
