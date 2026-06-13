from federated_coordinator.data import make_partitions, pooled_test
from federated_coordinator.federated import (
    comparison_report,
    run_centralized,
    run_federated,
    run_local_only,
)


def test_partitions_are_non_iid() -> None:
    partitions = make_partitions(seed=7)
    assert len(partitions) == 5
    # Different clusters fit noticeably different local models.
    from federated_coordinator.model import LinearModel

    weights = []
    for p in partitions:
        m = LinearModel(n_features=p.x_train.shape[1])
        m.fit(p.x_train, p.y_train, epochs=80)
        weights.append(m.weights.copy())
    # At least one pair of clusters differs in a coefficient by a clear margin.
    spread = max(abs(weights[i][3] - weights[j][3]) for i in range(5) for j in range(i + 1, 5))
    assert spread > 1.0


def test_federated_converges_and_beats_local_only() -> None:
    partitions = make_partitions(seed=7)
    model, history = run_federated(partitions, rounds=25, local_epochs=3, secure=True)
    # Loss trends down across rounds.
    assert history[-1].global_rmse < history[0].global_rmse

    x_test, y_test = pooled_test(partitions)
    federated_mse = model.evaluate(x_test, y_test)["mse"]
    local_only_mse = run_local_only(partitions)
    assert federated_mse < local_only_mse


def test_federated_approaches_centralized() -> None:
    partitions = make_partitions(seed=7)
    model, _ = run_federated(partitions, rounds=40, local_epochs=3, secure=True)
    x_test, y_test = pooled_test(partitions)
    federated_mse = model.evaluate(x_test, y_test)["mse"]
    centralized_mse = run_centralized(partitions).evaluate(x_test, y_test)["mse"]
    # Within a reasonable multiple of the no-privacy upper bound.
    assert federated_mse < centralized_mse * 1.6


def test_comparison_report_shape() -> None:
    report = comparison_report()  # default rounds — federated has converged
    assert report["clients"] == 5
    assert report["federated_beats_local_only"] is True
    assert "history" in report
