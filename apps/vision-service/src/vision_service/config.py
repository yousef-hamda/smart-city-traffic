"""Runtime configuration, sourced from the environment (12-factor)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings shared by every entrypoint of this service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "vision-service"
    port: int = 8082
    log_level: str = "INFO"
    otel_exporter_otlp_endpoint: str | None = None

    kafka_bootstrap_servers: str = "localhost:29092"
    frames_topic: str = "vision.frames"
    events_topic: str = "vision.events"
    consumer_group: str = "vision-service"

    redis_url: str = "redis://localhost:6379/0"

    # "synthetic" detects the simulator's rendered sprites with classical CV;
    # "yolo" runs Ultralytics YOLOv8 on real photographic footage. See README
    # for the tradeoff — COCO weights don't reliably fire on cartoon sprites.
    detector: str = "synthetic"
    yolo_weights: str = "yolov8n.pt"
    yolo_confidence: float = 0.35

    # Incident heuristics.
    stopped_seconds: float = 30.0
    assumed_fps: float = 15.0


settings = Settings()
