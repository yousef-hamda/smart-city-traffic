"""Exercise the real Flower NumPyClient contract without the Ray simulation."""

from federated_coordinator.flower_app import FlowerClient, build_strategy


def test_flower_client_fit_and_evaluate() -> None:
    client = FlowerClient(partition_id=0, local_epochs=5)
    params = client.get_parameters({})
    new_params, n, _ = client.fit(params, {})
    assert n > 0
    loss, n_test, metrics = client.evaluate(new_params, {})
    assert n_test > 0
    assert loss >= 0
    assert "rmse" in metrics


def test_build_strategy_has_initial_parameters() -> None:
    strategy = build_strategy(num_features=4)
    assert strategy.initial_parameters is not None
