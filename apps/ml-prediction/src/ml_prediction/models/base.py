"""Base protocol that every model must satisfy."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import numpy as np
import pandas as pd


@runtime_checkable
class BaseModel(Protocol):
    """Common interface for all ML models in this service."""

    model_version: str

    def train(self, df: pd.DataFrame) -> None: ...

    def predict(self, X: pd.DataFrame) -> np.ndarray[Any, np.dtype[np.float64]]: ...

    def save(self, path: Path) -> None: ...

    def load(self, path: Path) -> None: ...
