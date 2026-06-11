"""Runtime configuration, sourced from the environment (12-factor)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings shared by every entrypoint of this service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "vision-service"
    port: int = 8082
    log_level: str = "INFO"
    otel_exporter_otlp_endpoint: str | None = None


settings = Settings()
