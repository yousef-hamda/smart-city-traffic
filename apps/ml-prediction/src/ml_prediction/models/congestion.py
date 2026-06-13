"""LSTM (and Transformer scaffold) for short-horizon speed prediction.

Keeps TINY defaults so training completes in seconds on CPU:
- hidden_dim=32, 1 layer, 2 epochs max
- MC-dropout for confidence intervals
- Selectable via model_type="lstm" | "transformer"
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import lightning as L
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

logger = logging.getLogger(__name__)

FEATURES = ["vehicle_count", "avg_speed_kmh", "occupancy_pct", "hour", "is_rush"]
TARGET = "avg_speed_kmh"
SEQ_LEN = 6
MODEL_VERSION_LSTM = "lstm-congestion-v1"
MODEL_VERSION_TRANSFORMER = "transformer-congestion-v1"


# ---------------------------------------------------------------------------
# PyTorch modules
# ---------------------------------------------------------------------------

class _LSTMModule(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 32, dropout: float = 0.2) -> None:
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.drop = nn.Dropout(p=dropout)
        self.fc = nn.Linear(hidden_dim, 3)  # [15min, 30min, 60min] speeds

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        out = self.drop(out[:, -1, :])
        return self.fc(out)  # type: ignore[no-any-return]


class _TransformerModule(nn.Module):
    """Minimal Transformer encoder scaffold (Phase-2 experiment)."""
    def __init__(
        self, input_dim: int, d_model: int = 32, nhead: int = 2, dropout: float = 0.2
    ) -> None:
        super().__init__()
        self.proj = nn.Linear(input_dim, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, batch_first=True, dropout=dropout
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=1)
        self.drop = nn.Dropout(p=dropout)
        self.fc = nn.Linear(d_model, 3)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.proj(x)
        x = self.encoder(x)
        x = self.drop(x[:, -1, :])
        return self.fc(x)  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Lightning module
# ---------------------------------------------------------------------------

class _LightningModel(L.LightningModule):
    def __init__(self, net: nn.Module) -> None:
        super().__init__()
        self.net = net
        self.loss_fn = nn.MSELoss()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)  # type: ignore[no-any-return]

    def training_step(
        self, batch: tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> torch.Tensor:
        x, y = batch
        pred = self(x)
        loss: torch.Tensor = self.loss_fn(pred, y)
        self.log("train_loss", loss, prog_bar=False)
        return loss

    def configure_optimizers(self) -> torch.optim.Adam:
        return torch.optim.Adam(self.parameters(), lr=1e-3)


# ---------------------------------------------------------------------------
# Public model wrapper
# ---------------------------------------------------------------------------

class CongestionModel:
    """Wraps LSTM or Transformer for congestion speed prediction."""

    def __init__(self, model_type: str = "lstm", hidden_dim: int = 32) -> None:
        self.model_type = model_type
        self.hidden_dim = hidden_dim
        self.model_version: str = (
            MODEL_VERSION_LSTM if model_type == "lstm" else MODEL_VERSION_TRANSFORMER
        )
        self._net: nn.Module | None = None
        self._lightning: _LightningModel | None = None
        self._feature_mean: np.ndarray[Any, np.dtype[np.float64]] | None = None
        self._feature_std: np.ndarray[Any, np.dtype[np.float64]] | None = None
        self._n_features: int = len(FEATURES)

    def _build_net(self) -> nn.Module:
        if self.model_type == "transformer":
            return _TransformerModule(self._n_features, d_model=self.hidden_dim)
        return _LSTMModule(self._n_features, hidden_dim=self.hidden_dim)

    def _make_sequences(
        self, df: pd.DataFrame
    ) -> tuple[np.ndarray[Any, np.dtype[np.float64]], np.ndarray[Any, np.dtype[np.float64]]]:
        """Build (X, y) sliding-window sequences."""
        available = [c for c in FEATURES if c in df.columns]
        arr = df[available].fillna(0.0).values.astype(np.float32)

        # Normalize
        if self._feature_mean is None:
            self._feature_mean = arr.mean(axis=0)
            self._feature_std = arr.std(axis=0) + 1e-8
        arr = (arr - self._feature_mean) / self._feature_std

        speed_idx = available.index("avg_speed_kmh") if "avg_speed_kmh" in available else 0

        Xs, ys = [], []
        for i in range(SEQ_LEN, len(arr)):
            Xs.append(arr[i - SEQ_LEN : i])
            speed_now = arr[i, speed_idx]
            ys.append([speed_now, speed_now * 0.95, speed_now * 0.85])  # horizon proxies
        return np.array(Xs, dtype=np.float32), np.array(ys, dtype=np.float32)

    def train(self, df: pd.DataFrame) -> None:
        self._n_features = len([c for c in FEATURES if c in df.columns])
        X, y = self._make_sequences(df)
        if len(X) < 4:
            # Degenerate dataset — skip training
            logger.warning(
                "CongestionModel: not enough data (%d rows), using random weights", len(df)
            )
            self._net = self._build_net()
            self._lightning = _LightningModel(self._net)
            return

        Xt = torch.tensor(X)
        yt = torch.tensor(y)
        dataset = TensorDataset(Xt, yt)
        loader = DataLoader(dataset, batch_size=min(32, len(dataset)), shuffle=True)

        self._net = self._build_net()
        self._lightning = _LightningModel(self._net)

        trainer = L.Trainer(
            max_epochs=2,
            enable_progress_bar=False,
            enable_model_summary=False,
            logger=False,
            accelerator="cpu",
        )
        trainer.fit(self._lightning, loader)
        self._net = self._lightning.net
        logger.info("CongestionModel (%s) trained on %d sequences", self.model_type, len(X))

    def predict(self, X: pd.DataFrame) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Predict mean speed for a dataframe of readings."""
        result = self._predict_with_ci(X)
        return np.array([result["mean"]], dtype=np.float64)

    def predict_speed(
        self, recent_df: pd.DataFrame, n_mc: int = 20
    ) -> dict[str, float]:
        """Predict speed with MC-dropout confidence interval."""
        return self._predict_with_ci(recent_df, n_mc=n_mc)

    def _predict_with_ci(
        self, df: pd.DataFrame, n_mc: int = 20
    ) -> dict[str, float]:
        if self._net is None or self._lightning is None:
            # Not yet trained — return defaults
            return {"mean": 40.0, "lower": 30.0, "upper": 50.0}

        available = [c for c in FEATURES if c in df.columns]
        arr = df[available].fillna(0.0).values.astype(np.float32)

        if self._feature_mean is not None and self._feature_std is not None:
            arr = (arr - self._feature_mean) / self._feature_std

        # Pad or trim to SEQ_LEN
        if len(arr) < SEQ_LEN:
            pad = np.zeros((SEQ_LEN - len(arr), arr.shape[1]), dtype=np.float32)
            arr = np.vstack([pad, arr])
        arr = arr[-SEQ_LEN:]

        x = torch.tensor(arr).unsqueeze(0)  # [1, SEQ_LEN, features]

        # Enable MC-dropout for uncertainty
        self._net.train()
        preds = []
        with torch.no_grad():
            for _ in range(n_mc):
                out = self._lightning(x)  # [1, 3]
                preds.append(out[0, 0].item())  # 15-min horizon speed
        self._net.eval()

        preds_arr = np.array(preds)
        mean_speed = float(preds_arr.mean())
        std_speed = float(preds_arr.std())

        # De-normalize if needed (speed is normalized)
        speed_idx = available.index("avg_speed_kmh") if "avg_speed_kmh" in available else 0
        if self._feature_mean is not None and self._feature_std is not None:
            mean_speed = (
                mean_speed * float(self._feature_std[speed_idx])
                + float(self._feature_mean[speed_idx])
            )
            std_speed = std_speed * float(self._feature_std[speed_idx])

        return {
            "mean": max(4.0, mean_speed),
            "lower": max(4.0, mean_speed - 1.96 * std_speed),
            "upper": max(4.0, mean_speed + 1.96 * std_speed),
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_type": self.model_type,
                "hidden_dim": self.hidden_dim,
                "n_features": self._n_features,
                "feature_mean": self._feature_mean,
                "feature_std": self._feature_std,
                "state_dict": self._net.state_dict() if self._net else None,
            },
            path,
        )
        logger.info("CongestionModel saved to %s", path)

    def load(self, path: Path) -> None:
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        self.model_type = checkpoint["model_type"]
        self.hidden_dim = checkpoint["hidden_dim"]
        self._n_features = checkpoint["n_features"]
        self._feature_mean = checkpoint["feature_mean"]
        self._feature_std = checkpoint["feature_std"]
        self._net = self._build_net()
        if checkpoint["state_dict"] is not None:
            self._net.load_state_dict(checkpoint["state_dict"])
        self._lightning = _LightningModel(self._net)
        self._net.eval()
        logger.info("CongestionModel loaded from %s", path)
