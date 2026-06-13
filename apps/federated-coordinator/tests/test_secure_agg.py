import numpy as np

from federated_coordinator.secure_agg import aggregate, mask_updates


def _updates() -> list[list[np.ndarray]]:
    rng = np.random.default_rng(1)
    return [[rng.normal(size=4), rng.normal(size=1)] for _ in range(5)]


def test_masking_preserves_sum() -> None:
    updates = _updates()
    masked = mask_updates(updates, seed=3)
    plain_sum = [sum(u[layer] for u in updates) for layer in range(2)]
    masked_sum = [sum(m[layer] for m in masked) for layer in range(2)]
    for p, m in zip(plain_sum, masked_sum, strict=True):
        assert np.allclose(p, m, atol=1e-9)


def test_masking_hides_individual_updates() -> None:
    updates = _updates()
    masked = mask_updates(updates, seed=3)
    # At least one client's transmitted vector differs from its true update.
    differs = any(not np.allclose(updates[i][0], masked[i][0]) for i in range(len(updates)))
    assert differs


def test_secure_and_plain_aggregate_match() -> None:
    updates = _updates()
    counts = [10, 20, 30, 40, 50]
    secure = aggregate(updates, counts, secure=True)
    plain = aggregate(updates, counts, secure=False)
    for s, p in zip(secure, plain, strict=True):
        assert np.allclose(s, p, atol=1e-9)
