"""FedAvg orchestration plus the centralized and local-only baselines.

The comparison report tells the privacy/accuracy story: federated training
keeps every cluster's data local yet reaches accuracy close to the centralized
model that sees everything, and clearly beats training on any single cluster
alone (the non-IID penalty). The same model + data feed the real Flower client
in ``flower_app`` — this loop is the framework-free reference used by the
service endpoint, the report, and the tests.
"""

from dataclasses import dataclass

from federated_coordinator.data import (
    Partition,
    make_partitions,
    pooled_test,
    pooled_train,
)
from federated_coordinator.model import LinearModel, Parameters
from federated_coordinator.secure_agg import aggregate


@dataclass
class RoundMetric:
    round: int
    global_mse: float
    global_rmse: float


def _client_fit(global_params: Parameters, partition: Partition, epochs: int) -> Parameters:
    model = LinearModel(n_features=partition.x_train.shape[1])
    model.set_parameters(global_params)
    model.fit(partition.x_train, partition.y_train, epochs=epochs)
    return model.get_parameters()


def run_federated(
    partitions: list[Partition],
    rounds: int = 25,
    local_epochs: int = 3,
    secure: bool = True,
) -> tuple[LinearModel, list[RoundMetric]]:
    """FedAvg: each round, clients fit locally and the server aggregates."""
    n_features = partitions[0].x_train.shape[1]
    global_model = LinearModel(n_features=n_features)
    x_test, y_test = pooled_test(partitions)
    history: list[RoundMetric] = []

    for r in range(1, rounds + 1):
        params = global_model.get_parameters()
        updates = [_client_fit(params, p, local_epochs) for p in partitions]
        counts = [len(p.y_train) for p in partitions]
        global_model.set_parameters(aggregate(updates, counts, secure=secure))

        metrics = global_model.evaluate(x_test, y_test)
        history.append(RoundMetric(r, metrics["mse"], metrics["rmse"]))

    return global_model, history


def run_centralized(partitions: list[Partition], epochs: int = 60) -> LinearModel:
    """Upper-bound baseline: train on the pooled data (no privacy)."""
    x, y = pooled_train(partitions)
    model = LinearModel(n_features=x.shape[1])
    model.fit(x, y, epochs=epochs)
    return model


def run_local_only(partitions: list[Partition], epochs: int = 60) -> float:
    """Average global-test MSE of models trained on one cluster each."""
    x_test, y_test = pooled_test(partitions)
    mses = []
    for p in partitions:
        model = LinearModel(n_features=p.x_train.shape[1])
        model.fit(p.x_train, p.y_train, epochs=epochs)
        mses.append(model.evaluate(x_test, y_test)["mse"])
    return float(sum(mses) / len(mses))


def comparison_report(
    rounds: int = 25, local_epochs: int = 3, secure: bool = True, seed: int = 7
) -> dict[str, object]:
    """Run all three regimes and summarize the accuracy/privacy tradeoff."""
    partitions = make_partitions(seed=seed)
    x_test, y_test = pooled_test(partitions)

    federated_model, history = run_federated(partitions, rounds, local_epochs, secure)
    federated_mse = federated_model.evaluate(x_test, y_test)["mse"]
    centralized_mse = run_centralized(partitions).evaluate(x_test, y_test)["mse"]
    local_only_mse = run_local_only(partitions)

    gap = (federated_mse - centralized_mse) / centralized_mse if centralized_mse else 0.0
    return {
        "clients": len(partitions),
        "rounds": rounds,
        "secure_aggregation": secure,
        "centralized_mse": round(centralized_mse, 3),
        "federated_mse": round(federated_mse, 3),
        "local_only_mse": round(local_only_mse, 3),
        "federated_vs_centralized_gap_pct": round(100 * gap, 1),
        "federated_beats_local_only": federated_mse < local_only_mse,
        "history": [{"round": m.round, "rmse": round(m.global_rmse, 3)} for m in history],
    }
