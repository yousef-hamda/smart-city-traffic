"""Runtime configuration, sourced from the environment (12-factor)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings shared by every entrypoint of this service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "ai-assistant"
    port: int = 8086
    log_level: str = "INFO"
    otel_exporter_otlp_endpoint: str | None = None

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    postgres_dsn: str = "postgresql://traffic:traffic_dev_password@localhost:5432/traffic"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_password: str = ""
    chroma_path: str | None = None


settings = Settings()
