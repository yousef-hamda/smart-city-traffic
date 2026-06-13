"""Non-IID data partitions, one per simulated neighborhood sensor cluster.

Each neighborhood has its own *true* relationship between conditions and speed
(different coefficients), so the partitions are non-IID — exactly the setting
where federated learning earns its keep: a model must generalize across
clusters without any cluster's raw data leaving it. The five neighborhoods mirror
real ones (Talpiot, Romema, …) for narrative, but the data is synthetic and
self-contained (no dependency on the other services' datasets).
"""

from dataclasses import dataclass

import numpy as np

NEIGHBORHOODS = ["talpiot", "romema", "rehavia", "ramot", "city-center"]
N_FEATURES = 4  # [hour_sin, hour_cos, is_weekend, occupancy]


@dataclass(frozen=True)
class Partition:
    name: str
    x_train: np.ndarray
    y_train: np.ndarray
    x_test: np.ndarray
    y_test: np.ndarray


def _true_coefficients(rng: np.random.Generator) -> tuple[np.ndarray, float]:
    # Base relationship shared by all + a neighborhood-specific perturbation,
    # so clusters are related but not identical (non-IID but learnable).
    base = np.array([-6.0, 3.0, 5.0, -25.0])
    perturb = rng.normal(0.0, 2.0, size=N_FEATURES)
    bias = float(rng.uniform(45.0, 60.0))
    return base + perturb, bias


def _sample(rng: np.random.Generator, n: int) -> np.ndarray:
    hour = rng.uniform(0, 24, size=n)
    return np.column_stack(
        [
            np.sin(2 * np.pi * hour / 24),
            np.cos(2 * np.pi * hour / 24),
            rng.binomial(1, 0.28, size=n).astype(float),
            rng.uniform(0.0, 1.0, size=n),  # occupancy fraction
        ]
    )


def make_partitions(
    num_clients: int = 5, samples_per_client: int = 400, seed: int = 7
) -> list[Partition]:
    """Build ``num_clients`` non-IID partitions with an 80/20 train/test split."""
    rng = np.random.default_rng(seed)
    partitions: list[Partition] = []
    for i in range(num_clients):
        name = NEIGHBORHOODS[i % len(NEIGHBORHOODS)]
        coef, bias = _true_coefficients(rng)
        x = _sample(rng, samples_per_client)
        noise = rng.normal(0.0, 1.5, size=samples_per_client)
        y = np.clip(x @ coef + bias + noise, 4.0, 90.0)

        split = int(0.8 * samples_per_client)
        partitions.append(
            Partition(
                name=name,
                x_train=x[:split],
                y_train=y[:split],
                x_test=x[split:],
                y_test=y[split:],
            )
        )
    return partitions


def pooled_train(partitions: list[Partition]) -> tuple[np.ndarray, np.ndarray]:
    """Concatenate every client's training data (the centralized baseline)."""
    x = np.vstack([p.x_train for p in partitions])
    y = np.concatenate([p.y_train for p in partitions])
    return x, y


def pooled_test(partitions: list[Partition]) -> tuple[np.ndarray, np.ndarray]:
    """Global held-out test set across all neighborhoods."""
    x = np.vstack([p.x_test for p in partitions])
    y = np.concatenate([p.y_test for p in partitions])
    return x, y
