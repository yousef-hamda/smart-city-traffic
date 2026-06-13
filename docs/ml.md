# Machine Learning

The platform's prediction and learning layers: classical + deep forecasting
(ml-prediction), explainability (SHAP), the Feast feature store, and
privacy-preserving federated training (federated-coordinator).

## Models (ml-prediction)

| Model                   | Algorithm                | Predicts                              | Notes                           |
| ----------------------- | ------------------------ | ------------------------------------- | ------------------------------- |
| Demand forecaster       | XGBoost (+ Optuna HPO)   | next-hour vehicle count per segment   | strong tabular baseline         |
| Anomaly detector        | Isolation Forest         | is-anomaly + score on recent readings | unsupervised                    |
| Congestion forecaster   | LSTM (PyTorch Lightning) | next 15/30/60-min avg speed           | MC-dropout confidence band      |
| Congestion (experiment) | Transformer encoder      | same                                  | Phase-2 alternative to the LSTM |

All three are served behind **REST and gRPC** (`PredictionService` from
`packages/proto`). The model registry loads committed artifacts from
`ml/models/` or trains a small fixture on first run, so the service is
demoable without a separate training step.

### Training pipeline

```bash
python -m ml_prediction.train --model xgboost --data ml/data/training.csv
```

Logs params, metrics (MAE/RMSE), and artifacts to **MLflow** (local file
store). **Optuna** runs a small hyperparameter search for the XGBoost model.
Features are read from CSV by default or from **Feast** (`--features feast`).

### Synthetic data — and honesty

`ml/data/make_dataset.py` generates the training set from the sensor
simulator's demand model (the Israeli-week curve, hotspots, incidents), so the
data is realistic and self-contained. It is **simulated**, and the notebooks
and READMEs say so; the engineering value is the modelling pipeline, not the
data source.

### Explainability (SHAP)

Every prediction returns its **top-5 SHAP feature contributions** — TreeExplainer
for XGBoost, a KernelExplainer fallback for the neural models. The dashboard's
segment drill-down renders these as a "why this prediction?" panel, so a
forecast is auditable rather than a black box.

### Feature store (Feast)

`ml/feature_repo/` defines a `segment` entity and a FeatureView over the
engineered features. Online features (Redis) serve the live API; offline
features (parquet/Postgres) feed training — one definition, one source of
truth. `cd ml/feature_repo && feast apply`.

### Notebooks

`ml/notebooks/` (import the real `ml_prediction` package, load
`ml/data/training.csv`):

1. `01_eda` — distributions, the fundamental diagram, weekly rhythm
2. `02_features` — engineered time/lag features + correlations
3. `03_baseline_xgboost` — the tabular baseline + MAE/RMSE
4. `04_lstm_pytorch` — the LSTM congestion forecaster + uncertainty
5. `05_transformer_timeseries` — the Transformer experiment
6. `06_evaluation_and_shap` — evaluation + SHAP explanations
7. `07_feast_demo` — materialize and fetch features

## Federated learning (federated-coordinator)

Privacy-preserving training across five neighborhood clusters using the
**Flower** framework. The setting is **non-IID** (each neighborhood has its own
true speed/condition relationship), which is exactly where federated learning
earns its keep.

- **FedAvg** — each round, clients fit locally from the current global weights
  and the server takes a sample-weighted average. No raw data leaves a client.
- **Secure aggregation** — pairwise additive masking so masks cancel in the
  sum: the server only ever sees the aggregate, never an individual client's
  update. (Flower's `SecAggPlusWorkflow` is the production equivalent that also
  handles client dropouts.)
- **Result** — federated training matches the centralized (no-privacy) model's
  accuracy within ~0% on the global test set while keeping every cluster's data
  local, and clearly beats training on any single cluster alone.

```bash
python -m federated_coordinator.train --rounds 25      # local FedAvg loop
python -m federated_coordinator.train --backend flower  # real Flower engine
```

See [`docs/rl.md`](rl.md) for the reinforcement-learning signal optimizer.
