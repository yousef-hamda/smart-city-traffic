"""Runtime configuration, sourced from the environment (12-factor)."""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    """Environment-driven settings shared by every entrypoint of this service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "ml-prediction"
    port: int = 8083
    log_level: str = "INFO"
    otel_exporter_otlp_endpoint: str | None = None

    # ML model artifacts
    model_dir: Path = _repo_root() / "ml" / "models"

    # MLflow
    mlflow_tracking_uri: str = "file://" + str(_repo_root() / "mlruns")

    # Redis (optional — not required by default)
    redis_url: str = "redis://localhost:6379/1"

    # Postgres (optional)
    postgres_dsn: str = "postgresql://traffic:traffic_dev_password@localhost:5432/traffic"

    # gRPC
    grpc_port: int = 9093

    # Feast feature store
    feast_repo_path: Path = _repo_root() / "ml" / "feature_repo"


settings = Settings()
