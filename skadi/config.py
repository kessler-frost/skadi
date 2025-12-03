"""Configuration management for Skadi using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Provider Configuration
    skadi_api_key: str | None = None
    skadi_model: str = "anthropic/claude-haiku-4.5"
    skadi_base_url: str | None = (
        None  # If None, uses OpenRouter; otherwise uses custom provider
    )

    # Backend Configuration
    default_backend: str = "default.qubit"
    default_shots: int | None = None

    # AWS Configuration (for Braket)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "us-east-1"
    aws_braket_s3_bucket: str | None = None
    aws_braket_s3_prefix: str = "skadi-results"


# Global settings instance
settings = Settings()
