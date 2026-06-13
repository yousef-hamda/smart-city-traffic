"""SHAP-based feature importance for model predictions."""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

ShapContribution = dict[str, Any]


def explain_xgboost(
    model: Any, X: pd.DataFrame, feature_names: list[str] | None = None
) -> list[ShapContribution]:
    """Return top-5 SHAP contributions for an XGBoost model prediction."""
    import shap

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        cols = feature_names or list(X.columns)
        mean_abs = np.abs(shap_values).mean(axis=0) if shap_values.ndim > 1 else np.abs(shap_values)

        top_idx = np.argsort(-mean_abs)[:5]
        return [
            {"feature": cols[i], "value": float(mean_abs[i])}
            for i in top_idx
        ]
    except Exception as exc:
        logger.warning("SHAP TreeExplainer failed: %s — falling back to feature names", exc)
        return _fallback_shap(X, feature_names)


def explain_neural(
    model: Any, X: pd.DataFrame, feature_names: list[str] | None = None
) -> list[ShapContribution]:
    """Return top-5 SHAP contributions for neural/sklearn models via KernelExplainer."""
    import shap

    cols = feature_names or list(X.columns)

    def _predict(x: np.ndarray[Any, np.dtype[np.float32]]) -> np.ndarray[Any, np.dtype[np.float32]]:
        df = pd.DataFrame(x, columns=cols[: x.shape[1]])
        result: np.ndarray[Any, np.dtype[np.float32]] = model.predict(df)
        return result.reshape(-1, 1) if result.ndim == 1 else result

    try:
        background = shap.sample(X, min(50, len(X)))
        explainer = shap.KernelExplainer(_predict, background)
        shap_values = explainer.shap_values(X.iloc[:1], nsamples=50, silent=True)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        mean_abs = np.abs(shap_values).flatten()[: len(cols)]
        sorted_idx = np.argsort(-mean_abs)[:5]
        return [
            {"feature": cols[i], "value": float(mean_abs[i])}
            for i in sorted_idx
        ]
    except Exception as exc:
        logger.warning("SHAP KernelExplainer failed: %s — using fallback", exc)
        return _fallback_shap(X, feature_names)


def _fallback_shap(
    X: pd.DataFrame, feature_names: list[str] | None = None
) -> list[ShapContribution]:
    """Return placeholder SHAP contributions based on feature variance."""
    variances = X.var(numeric_only=True)
    top5 = variances.nlargest(5)
    return [
        {"feature": str(name), "value": float(val)}
        for name, val in top5.items()
    ]


def get_top5_shap(
    model: Any,
    X: pd.DataFrame,
    model_type: str = "xgboost",
    feature_names: list[str] | None = None,
) -> list[ShapContribution]:
    """Dispatch to correct SHAP explainer based on model type.

    Always returns exactly 5 contributions.
    """
    if len(X.columns) == 0:
        return [{"feature": f"feature_{i}", "value": 0.0} for i in range(5)]

    if model_type == "xgboost":
        contributions = explain_xgboost(model, X, feature_names)
    else:
        contributions = explain_neural(model, X, feature_names)

    # Pad to exactly 5
    while len(contributions) < 5:
        contributions.append({"feature": f"feature_{len(contributions)}", "value": 0.0})

    return contributions[:5]
