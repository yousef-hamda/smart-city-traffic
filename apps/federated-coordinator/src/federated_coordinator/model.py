"""A tiny linear model whose parameters are plain numpy arrays.

Linear regression keeps the federated-learning machinery legible: the
"weights" exchanged each round are just ``[w, b]`` arrays, so FedAvg is a
weighted mean of arrays and secure aggregation is masking of arrays. The point
of this service is the *protocol* (federated rounds, secure aggregation,
non-IID partitions), not the model's sophistication.
"""

from dataclasses import dataclass, field
from typing import cast

import numpy as np

Parameters = list[np.ndarray]


@dataclass
class LinearModel:
    """Ridge-regularized linear regressor trained by gradient descent."""

    n_features: int
    learning_rate: float = 0.05
    l2: float = 1e-4
    weights: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.float64))
    bias: float = 0.0

    def __post_init__(self) -> None:
        if self.weights.size == 0:
            self.weights = np.zeros(self.n_features, dtype=np.float64)

    # --- parameter exchange (the values that travel between client/server) ---
    def get_parameters(self) -> Parameters:
        return [self.weights.copy(), np.array([self.bias], dtype=np.float64)]

    def set_parameters(self, params: Parameters) -> None:
        self.weights = params[0].astype(np.float64).copy()
        self.bias = float(params[1][0])

    # --- training / evaluation ---
    def fit(self, x: np.ndarray, y: np.ndarray, epochs: int = 5) -> None:
        n = len(y)
        for _ in range(epochs):
            preds = x @ self.weights + self.bias
            error = preds - y
            grad_w = (x.T @ error) / n + self.l2 * self.weights
            grad_b = float(np.mean(error))
            self.weights -= self.learning_rate * grad_w
            self.bias -= self.learning_rate * grad_b

    def predict(self, x: np.ndarray) -> np.ndarray:
        return cast(np.ndarray, x @ self.weights + self.bias)

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> dict[str, float]:
        preds = self.predict(x)
        residual = preds - y
        mse = float(np.mean(residual**2))
        mae = float(np.mean(np.abs(residual)))
        return {"mse": mse, "mae": mae, "rmse": mse**0.5}
