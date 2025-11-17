"""Configuration management for Skadi using pydantic-settings."""

from typing import Optional

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
    skadi_api_key: str
    skadi_model: str = "anthropic/claude-haiku-4.5"
    skadi_base_url: Optional[str] = (
        None  # If None, uses OpenRouter; otherwise uses custom provider
    )


# Global settings instance
settings = Settings()
