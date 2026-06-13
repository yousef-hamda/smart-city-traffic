"""Pairwise-masking secure aggregation.

Plain FedAvg sends each client's raw weights to the server, which can leak
information about a client's local data. Secure aggregation lets the server
learn only the *sum* (hence the average) of the updates, never any individual
update.

This implements the core idea concretely: every pair of clients (i, j) agrees
on a shared random mask ``m_ij``. Client i adds it, client j subtracts it, so
across the full set every mask cancels and ``sum(masked) == sum(plain)`` — yet
each transmitted vector is indistinguishable from random. Flower ships a
production implementation (``SecAggPlusWorkflow``) that also handles dropouts
via secret sharing; this module is the legible reference the report explains.
"""

import numpy as np

from federated_coordinator.model import Parameters


def _flatten(params: Parameters) -> tuple[np.ndarray, list[tuple[int, ...]]]:
    shapes = [p.shape for p in params]
    flat = np.concatenate([p.ravel() for p in params])
    return flat, shapes


def _unflatten(flat: np.ndarray, shapes: list[tuple[int, ...]]) -> Parameters:
    out: Parameters = []
    offset = 0
    for shape in shapes:
        size = int(np.prod(shape))
        out.append(flat[offset : offset + size].reshape(shape))
        offset += size
    return out


def mask_updates(updates: list[Parameters], seed: int = 0) -> list[Parameters]:
    """Return masked updates whose elementwise sum equals the unmasked sum."""
    rng = np.random.default_rng(seed)
    flats = [_flatten(u) for u in updates]
    vectors = [f[0].copy() for f in flats]
    shapes = flats[0][1]
    n = len(updates)

    for i in range(n):
        for j in range(i + 1, n):
            mask = rng.normal(0.0, 100.0, size=vectors[i].shape)
            vectors[i] += mask  # i adds
            vectors[j] -= mask  # j subtracts → cancels in the sum

    return [_unflatten(v, shapes) for v in vectors]


def aggregate(
    updates: list[Parameters], sample_counts: list[int], secure: bool = True
) -> Parameters:
    """Weighted FedAvg over client updates, optionally with secure masking.

    Masking is applied to a *copy* with weighting folded in, so the masked
    vectors still sum to the weighted average. With ``secure=True`` the server
    only ever touches masked vectors.
    """
    total = float(sum(sample_counts))
    weighted = [
        [layer * (count / total) for layer in update]
        for update, count in zip(updates, sample_counts, strict=True)
    ]

    if secure:
        weighted = mask_updates(weighted)

    n_layers = len(weighted[0])
    return [
        np.sum([weighted[c][layer] for c in range(len(weighted))], axis=0)
        for layer in range(n_layers)
    ]
