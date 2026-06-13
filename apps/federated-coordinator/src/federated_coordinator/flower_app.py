"""Flower (flwr) integration: NumPyClient workers + a FedAvg ServerApp.

This is the genuine Flower-framework wiring the spec calls for. Each simulated
sensor cluster becomes a ``FlowerClient`` over its non-IID partition; the server
runs FedAvg. The framework-free loop in ``federated`` is the same algorithm and
is what the service/report/tests use by default (it needs no Ray runtime and is
deterministic); ``run_flower_simulation`` drives the real Flower engine and
falls back to that loop if the simulation backend is unavailable.
"""

from typing import Any

import structlog
from flwr.client import ClientApp, NumPyClient
from flwr.common import Context, Scalar, ndarrays_to_parameters
from flwr.server import ServerApp, ServerAppComponents, ServerConfig
from flwr.server.strategy import FedAvg

from federated_coordinator.data import make_partitions
from federated_coordinator.model import LinearModel, Parameters

logger = structlog.get_logger()


class FlowerClient(NumPyClient):
    """A single neighborhood cluster training locally on its own data."""

    def __init__(self, partition_id: int, local_epochs: int = 3) -> None:
        partitions = make_partitions()
        self._p = partitions[partition_id % len(partitions)]
        self._model = LinearModel(n_features=self._p.x_train.shape[1])
        self._local_epochs = local_epochs

    def get_parameters(self, config: dict[str, Any]) -> Parameters:
        return self._model.get_parameters()

    def fit(
        self, parameters: Parameters, config: dict[str, Any]
    ) -> tuple[Parameters, int, dict[str, Scalar]]:
        self._model.set_parameters(parameters)
        self._model.fit(self._p.x_train, self._p.y_train, epochs=self._local_epochs)
        return self._model.get_parameters(), len(self._p.y_train), {}

    def evaluate(
        self, parameters: Parameters, config: dict[str, Any]
    ) -> tuple[float, int, dict[str, Scalar]]:
        self._model.set_parameters(parameters)
        metrics = self._model.evaluate(self._p.x_test, self._p.y_test)
        return metrics["mse"], len(self._p.y_test), {"rmse": metrics["rmse"]}


def client_fn(context: Context) -> Any:
    partition_id = int(context.node_config.get("partition-id", 0))
    return FlowerClient(partition_id).to_client()


def build_strategy(num_features: int = 4) -> FedAvg:
    initial = LinearModel(n_features=num_features).get_parameters()
    return FedAvg(
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_available_clients=5,
        initial_parameters=ndarrays_to_parameters(initial),
    )


def server_fn(context: Context) -> ServerAppComponents:
    num_rounds = int(context.run_config.get("num-rounds", 20))
    return ServerAppComponents(
        strategy=build_strategy(), config=ServerConfig(num_rounds=num_rounds)
    )


client_app = ClientApp(client_fn=client_fn)
server_app = ServerApp(server_fn=server_fn)


def run_flower_simulation(num_clients: int = 5, num_rounds: int = 20) -> dict[str, object]:
    """Run the real Flower simulation; fall back to the local loop on failure."""
    try:
        from flwr.simulation import run_simulation

        run_simulation(
            server_app=server_app,
            client_app=client_app,
            num_supernodes=num_clients,
        )
        return {"backend": "flower", "clients": num_clients, "rounds": num_rounds}
    except Exception as exc:  # noqa: BLE001 - Ray/backend may be unavailable
        logger.warning("flower_simulation_unavailable", error=str(exc))
        from federated_coordinator.federated import comparison_report

        report = comparison_report(rounds=num_rounds)
        report["backend"] = "local-fallback"
        return report
