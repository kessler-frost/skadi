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

    # OpenAI Configuration (for embeddings)
    openai_api_key: Optional[str] = None

    # Knowledge Base Configuration
    use_knowledge: bool = True
    use_pennylane_kb: bool = True
    use_context7: bool = True
    max_knowledge_tokens: int = 2000

    # Database Configuration
    lancedb_uri: str = "data/lancedb"
    lancedb_table: str = "pennylane_knowledge"

    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Web Scraping Configuration
    scraper_output_dir: str = "data/pennylane_docs"
    scraper_chunk_size_tokens: int = 750
    scraper_chunk_overlap_tokens: int = 100
    scraper_rate_limit_seconds: float = 1.0


# Global settings instance
settings = Settings()
