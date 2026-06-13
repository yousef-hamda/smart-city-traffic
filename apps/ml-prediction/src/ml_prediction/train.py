"""Training pipeline CLI.

Usage:
    python -m ml_prediction.train --model xgboost --data ml/data/training.csv --no-mlflow
    python -m ml_prediction.train --model lstm --features csv
    python -m ml_prediction.train --model isoforest --no-mlflow
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _load_data(data_path: Path) -> pd.DataFrame:
    if not data_path.exists():
        logger.warning("Training data not found at %s — generating on the fly...", data_path)
        data_path.parent.mkdir(parents=True, exist_ok=True)
        repo_root = _get_repo_root()
        make_script = repo_root / "ml" / "data" / "make_dataset.py"
        import subprocess

        result = subprocess.run(
            [sys.executable, str(make_script)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"make_dataset.py failed: {result.stderr}")

    df = pd.read_csv(data_path)
    logger.info("Loaded %d rows from %s", len(df), data_path)
    return df


def _train_xgboost(
    df: pd.DataFrame, model_dir: Path, use_mlflow: bool
) -> Path:
    import optuna

    from ml_prediction.models.demand import FEATURES, TARGET, DemandModel

    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 20, 100),
            "max_depth": trial.suggest_int("max_depth", 2, 6),
            "learning_rate": trial.suggest_float("learning_rate", 0.05, 0.3),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        }
        model = DemandModel(params=params)
        # Simple hold-out split
        split = int(len(df) * 0.8)
        train_df, val_df = df.iloc[:split], df.iloc[split:]
        model.train(train_df)
        available = [c for c in FEATURES if c in val_df.columns]
        import numpy as np

        preds = model.predict(val_df[available])
        mae = float(np.mean(np.abs(preds - val_df[TARGET].values)))
        return mae

    study = optuna.create_study(
        direction="minimize", sampler=optuna.samplers.TPESampler(seed=42)
    )
    study.optimize(objective, n_trials=5, show_progress_bar=False)

    best_params = study.best_params
    logger.info("Best XGBoost params: %s, MAE=%.3f", best_params, study.best_value)

    # Train final model on all data
    final_model = DemandModel(params=best_params)
    final_model.train(df)

    artifact_path = model_dir / "demand_xgboost.joblib"
    final_model.save(artifact_path)

    if use_mlflow:
        import mlflow

        with mlflow.start_run(run_name="xgboost-demand"):
            mlflow.log_params(best_params)
            mlflow.log_metric("best_mae", study.best_value)
            mlflow.log_artifact(str(artifact_path))
    return artifact_path


def _train_isoforest(
    df: pd.DataFrame, model_dir: Path, use_mlflow: bool
) -> Path:
    from ml_prediction.models.anomaly import AnomalyModel

    model = AnomalyModel()
    model.train(df)
    artifact_path = model_dir / "anomaly_isoforest.joblib"
    model.save(artifact_path)

    if use_mlflow:
        import mlflow

        with mlflow.start_run(run_name="isoforest-anomaly"):
            mlflow.log_param("model", "IsolationForest")
            mlflow.log_artifact(str(artifact_path))
    return artifact_path


def _train_lstm(
    df: pd.DataFrame, model_dir: Path, use_mlflow: bool
) -> Path:
    from ml_prediction.models.congestion import CongestionModel

    model = CongestionModel(model_type="lstm")
    model.train(df)
    artifact_path = model_dir / "congestion_lstm.pt"
    model.save(artifact_path)

    if use_mlflow:
        import mlflow

        with mlflow.start_run(run_name="lstm-congestion"):
            mlflow.log_param("model_type", "lstm")
            mlflow.log_artifact(str(artifact_path))
    return artifact_path


def _train_transformer(
    df: pd.DataFrame, model_dir: Path, use_mlflow: bool
) -> Path:
    from ml_prediction.models.congestion import CongestionModel

    model = CongestionModel(model_type="transformer")
    model.train(df)
    artifact_path = model_dir / "congestion_transformer.pt"
    model.save(artifact_path)

    if use_mlflow:
        import mlflow

        with mlflow.start_run(run_name="transformer-congestion"):
            mlflow.log_param("model_type", "transformer")
            mlflow.log_artifact(str(artifact_path))
    return artifact_path


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="Train traffic prediction models")
    parser.add_argument(
        "--model",
        choices=["xgboost", "lstm", "transformer", "isoforest"],
        default="xgboost",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("ml/data/training.csv"),
    )
    parser.add_argument(
        "--features",
        choices=["feast", "csv"],
        default="csv",
    )
    parser.add_argument("--no-mlflow", action="store_true", default=False)
    args = parser.parse_args(argv)

    use_mlflow = not args.no_mlflow
    repo_root = _get_repo_root()
    model_dir = repo_root / "ml" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    # Resolve data path relative to repo root if not absolute
    data_path: Path = args.data if args.data.is_absolute() else repo_root / args.data

    if args.features == "feast":
        logger.info("Feature source: feast (falling back to CSV for now)")

    df = _load_data(data_path)

    if use_mlflow:
        import mlflow

        mlflow_uri = str(repo_root / "mlruns")
        mlflow.set_tracking_uri(f"file://{mlflow_uri}")
        mlflow.set_experiment("smart-city-traffic")

    if args.model == "xgboost":
        artifact = _train_xgboost(df, model_dir, use_mlflow)
    elif args.model == "isoforest":
        artifact = _train_isoforest(df, model_dir, use_mlflow)
    elif args.model == "lstm":
        artifact = _train_lstm(df, model_dir, use_mlflow)
    elif args.model == "transformer":
        artifact = _train_transformer(df, model_dir, use_mlflow)
    else:
        raise ValueError(f"Unknown model: {args.model}")

    print(f"Artifact saved: {artifact}")


if __name__ == "__main__":
    main()
