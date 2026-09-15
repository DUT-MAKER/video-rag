"""Configuration settings using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App configuration
    APP_NAME: str = "RAG Viral Video"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Self-Hosted LLM configuration
    LLM_API_BASE_URL: str = "http://localhost:8000/v1"
    LLM_API_KEY: str = "dummy-key"
    LLM_MODEL_NAME: str = "default"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048

    # Self-Hosted Embedding configuration
    EMBEDDING_API_BASE_URL: str = "http://localhost:8000/v1"
    EMBEDDING_API_KEY: str = "dummy-key"
    EMBEDDING_MODEL_NAME: str = "default-embed"
    EMBEDDING_DIMENSION: int = 384

    # ChromaDB configuration
    CHROMA_PERSIST_DIR: str = "./data/storage/chroma"
    CHROMA_COLLECTION_NAME: str = "viral_video_patterns"

    # Fallback flag (allows local standalone testing without live external model endpoints)
    USE_LOCAL_FALLBACK: bool = True


@lru_cache
def get_settings() -> Settings:
    """Singleton getter for application settings."""
    return Settings()
