"""CLI: ``python -m federated_coordinator.train``.

    python -m federated_coordinator.train --rounds 30                # local FedAvg loop
    python -m federated_coordinator.train --backend flower           # real Flower engine
    python -m federated_coordinator.train --no-secure                # plain aggregation
"""

import json

import click
import structlog

from federated_coordinator.federated import comparison_report
from federated_coordinator.logging import configure_logging

logger = structlog.get_logger()


@click.command()
@click.option("--rounds", type=int, default=20, show_default=True)
@click.option("--local-epochs", type=int, default=3, show_default=True)
@click.option("--secure/--no-secure", default=True, help="Use secure aggregation.")
@click.option("--backend", type=click.Choice(["local", "flower"]), default="local",
              show_default=True, help="local FedAvg loop, or the real Flower simulation.")
def main(rounds: int, local_epochs: int, secure: bool, backend: str) -> None:
    """Run federated training and print the comparison report as JSON."""
    configure_logging()
    if backend == "flower":
        from federated_coordinator.flower_app import run_flower_simulation

        report = run_flower_simulation(num_rounds=rounds)
    else:
        report = comparison_report(rounds=rounds, local_epochs=local_epochs, secure=secure)
    click.echo(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
