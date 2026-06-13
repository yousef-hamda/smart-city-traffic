"""Runtime configuration, sourced from the environment (12-factor)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings shared by every entrypoint of this service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "voice-gateway"
    port: int = 8087
    log_level: str = "INFO"
    otel_exporter_otlp_endpoint: str | None = None
    ai_assistant_url: str = "http://localhost:8086"
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    whisper_model: str = "tiny"


settings = Settings()
