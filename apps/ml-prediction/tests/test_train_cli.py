"""Test the training CLI produces artifacts."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _make_df(n: int = 60) -> pd.DataFrame:
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


@pytest.mark.slow
def test_train_xgboost_produces_artifact(tmp_path: Path) -> None:
    """Training XGBoost CLI should produce a .joblib artifact."""
    df = _make_df()
    from ml_prediction.train import _train_xgboost

    model_dir = tmp_path / "models"
    model_dir.mkdir()
    artifact = _train_xgboost(df, model_dir, use_mlflow=False)
    assert artifact.exists(), f"Artifact not found: {artifact}"
    assert artifact.suffix == ".joblib"


@pytest.mark.slow
def test_train_isoforest_produces_artifact(tmp_path: Path) -> None:
    rng = np.random.default_rng(42)
    n = 60
    df = pd.DataFrame({
        "vehicle_count": rng.integers(10, 200, n).astype(float),
        "avg_speed_kmh": rng.uniform(10, 80, n),
        "occupancy_pct": rng.uniform(5, 90, n),
    })

    from ml_prediction.train import _train_isoforest

    model_dir = tmp_path / "models"
    model_dir.mkdir()
    artifact = _train_isoforest(df, model_dir, use_mlflow=False)
    assert artifact.exists()
    assert artifact.suffix == ".joblib"
