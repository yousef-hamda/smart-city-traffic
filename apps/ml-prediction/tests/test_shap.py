"""Unit tests for SHAP explainability."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _make_xgboost_model() -> tuple[object, pd.DataFrame]:
    from ml_prediction.models.demand import DemandModel

    rng = np.random.default_rng(42)
    n = 80
    hour_vals = np.arange(n) % 24
    dow_vals = np.arange(n) % 7
    df = pd.DataFrame({
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
    model = DemandModel()
    model.train(df)
    return model._model, df


class TestSHAP:
    def test_returns_exactly_5_contributions(self) -> None:
        from ml_prediction.explain import get_top5_shap
        from ml_prediction.models.demand import FEATURES

        xgb_model, df = _make_xgboost_model()
        available = [c for c in FEATURES if c in df.columns]
        X = df[available].fillna(0.0)
        contributions = get_top5_shap(xgb_model, X, model_type="xgboost", feature_names=available)
        assert len(contributions) == 5, f"Expected 5, got {len(contributions)}"

    def test_contribution_structure(self) -> None:
        from ml_prediction.explain import get_top5_shap
        from ml_prediction.models.demand import FEATURES

        xgb_model, df = _make_xgboost_model()
        available = [c for c in FEATURES if c in df.columns]
        X = df[available].fillna(0.0)
        contributions = get_top5_shap(xgb_model, X, model_type="xgboost", feature_names=available)
        for c in contributions:
            assert "feature" in c
            assert "value" in c
            assert isinstance(c["feature"], str)
            assert isinstance(c["value"], float)
            assert np.isfinite(c["value"])

    def test_fallback_returns_5(self) -> None:
        from ml_prediction.explain import get_top5_shap

        rng = np.random.default_rng(42)
        X = pd.DataFrame(rng.random((10, 6)), columns=[f"f{i}" for i in range(6)])
        # Pass a non-model object — should fall back to variance-based
        contributions = get_top5_shap(None, X, model_type="xgboost")
        assert len(contributions) == 5
