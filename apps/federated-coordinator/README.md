# Federated Learning Coordinator

Privacy-preserving model training across simulated sensor clusters using the
**Flower** framework. Each of five neighborhoods trains on its own data; only
model weight updates ever leave a client, and secure aggregation means the
server sees only their _sum_, never an individual update.

## Why it's here

Traffic data is sensitive and often can't be centralized across jurisdictions.
Federated learning trains a shared model without pooling raw data. This service
demonstrates the full protocol and quantifies the accuracy/privacy tradeoff
against the two baselines that bracket it.

## What it does

- **Non-IID partitions** (`data.py`) — five neighborhoods, each with its own
  true speed/condition relationship, so the setting is genuinely non-IID.
- **FedAvg** (`federated.py`) — each round, clients fit locally from the
  current global weights and the server takes a sample-weighted average. A
  framework-free reference loop powers the service, report, and tests
  deterministically.
- **Flower integration** (`flower_app.py`) — the same model wrapped as a real
  `flwr` `NumPyClient` with a `FedAvg` `ServerApp`; `--backend flower` runs the
  actual Flower engine (falls back to the loop if the Ray backend is absent).
- **Secure aggregation** (`secure_agg.py`) — pairwise additive masking so
  masks cancel in the sum: the server learns the aggregate, not any client's
  update. Flower's `SecAggPlusWorkflow` is the production equivalent (also
  handles dropouts via secret sharing); this is the legible reference.

## Results (default run, seed 7)

| Regime                              | Global-test MSE | Sees raw data of        |
| ----------------------------------- | --------------- | ----------------------- |
| Centralized (upper bound)           | ~112            | all clusters            |
| **Federated (FedAvg + secure agg)** | **~112**        | none — only weight sums |
| Local-only (per cluster, averaged)  | ~121            | one cluster             |

Federated matches the centralized model while keeping every cluster's data
local, and clearly beats training on any single cluster alone.

## Interfaces

| Kind | Endpoint                                | Notes                                         |
| ---- | --------------------------------------- | --------------------------------------------- |
| REST | `GET /health`                           | liveness                                      |
| REST | `POST /train/federated`                 | run a session, returns the comparison report  |
| REST | `GET /report`                           | most recent report                            |
| CLI  | `python -m federated_coordinator.train` | `--rounds`, `--no-secure`, `--backend flower` |

## Local development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m federated_coordinator.train --rounds 25
pytest -q && ruff check src tests && mypy src
```
