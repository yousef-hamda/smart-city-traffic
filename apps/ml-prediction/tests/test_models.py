"""Unit tests for ML models."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _make_df(n: int = 100) -> pd.DataFrame:
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


class TestDemandModel:
    def test_predict_shape(self) -> None:
        from ml_prediction.models.demand import DemandModel

        df = _make_df()
        model = DemandModel()
        model.train(df)
        preds = model.predict(df)
        assert preds.shape == (len(df),), f"Expected ({len(df)},), got {preds.shape}"

    def test_predict_nonnegative(self) -> None:
        from ml_prediction.models.demand import DemandModel

        df = _make_df()
        model = DemandModel()
        model.train(df)
        preds = model.predict(df)
        assert np.all(np.isfinite(preds)), "Predictions contain NaN/inf"

    def test_model_version_present(self) -> None:
        from ml_prediction.models.demand import DemandModel

        model = DemandModel()
        assert isinstance(model.model_version, str)
        assert len(model.model_version) > 0

    def test_save_load(self, tmp_path: Path) -> None:
        from ml_prediction.models.demand import DemandModel

        df = _make_df()
        model = DemandModel()
        model.train(df)
        p = tmp_path / "demand.joblib"
        model.save(p)
        assert p.exists()

        model2 = DemandModel()
        model2.load(p)
        preds1 = model.predict(df)
        preds2 = model2.predict(df)
        np.testing.assert_allclose(preds1, preds2, rtol=1e-5)


class TestAnomalyModel:
    def test_normal_not_flagged(self) -> None:
        from ml_prediction.models.anomaly import AnomalyModel

        df = _make_df(200)
        model = AnomalyModel()
        model.train(df)
        # Normal reading
        result = model.detect(
            {"avg_speed_kmh": 50.0, "occupancy_pct": 40.0, "vehicle_count": 100.0}
        )
        assert "is_anomaly" in result
        assert "score" in result
        assert isinstance(result["is_anomaly"], bool)

    def test_outlier_flagged(self) -> None:
        from ml_prediction.models.anomaly import AnomalyModel

        df = _make_df(200)
        model = AnomalyModel(contamination=0.1)
        model.train(df)
        # Extreme outlier — speed=0 with zero occupancy is anomalous
        result = model.detect(
            {"avg_speed_kmh": 0.001, "occupancy_pct": 0.001, "vehicle_count": 9999.0}
        )
        assert isinstance(result["is_anomaly"], bool)
        # Score should be finite
        assert np.isfinite(result["score"])

    def test_model_version_present(self) -> None:
        from ml_prediction.models.anomaly import AnomalyModel

        model = AnomalyModel()
        assert isinstance(model.model_version, str)
        assert len(model.model_version) > 0


@pytest.mark.slow
class TestCongestionModel:
    def test_predict_finite_speed(self) -> None:
        from ml_prediction.models.congestion import CongestionModel

        df = _make_df(60)
        model = CongestionModel(model_type="lstm")
        model.train(df)
        result = model.predict_speed(df)
        assert np.isfinite(result["mean"]), "Mean speed is not finite"
        assert result["mean"] > 0, "Mean speed must be positive"
        assert result["lower"] <= result["mean"] <= result["upper"]

    def test_speed_in_range(self) -> None:
        from ml_prediction.models.congestion import CongestionModel

        df = _make_df(60)
        model = CongestionModel(model_type="lstm")
        model.train(df)
        result = model.predict_speed(df)
        assert 0 < result["mean"] < 200, f"Speed {result['mean']} out of expected range"

    def test_model_version_present(self) -> None:
        from ml_prediction.models.congestion import CongestionModel

        model = CongestionModel(model_type="lstm")
        assert isinstance(model.model_version, str)
        assert len(model.model_version) > 0

    def test_save_load(self, tmp_path: Path) -> None:
        from ml_prediction.models.congestion import CongestionModel

        df = _make_df(60)
        model = CongestionModel()
        model.train(df)
        p = tmp_path / "congestion.pt"
        model.save(p)
        assert p.exists()

        model2 = CongestionModel()
        model2.load(p)
        assert model2.model_version == model.model_version
