"""Modular configuration settings for the application."""

from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent

_SETTINGS_CONFIG = SettingsConfigDict(
    env_file=ROOT_DIR / ".env",
    env_file_encoding="utf-8",
    extra="ignore",
    case_sensitive=False,
)


class AppSettings(BaseSettings):
    """Core application server configuration."""

    model_config = _SETTINGS_CONFIG

    name: str = Field(default="RAG Viral Video", validation_alias="APP_NAME")
    env: str = Field(default="development", validation_alias="APP_ENV")
    debug: bool = Field(default=True, validation_alias="DEBUG")
    host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    port: int = Field(default=8000, validation_alias="API_PORT")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="CORS_ORIGINS",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """Parses comma-separated CORS origins into a list."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


class DatabaseSettings(BaseSettings):
    """PostgreSQL and pgvector database settings."""

    model_config = _SETTINGS_CONFIG

    url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/boilerplate_db",
        validation_alias="DATABASE_URL",
    )



class AuthSettings(BaseSettings):
    """Authentication and JWT configuration."""

    model_config = _SETTINGS_CONFIG

    secret_key: str = Field(
        default="change-this-to-a-very-secure-secret-key-in-production",
        validation_alias="JWT_SECRET_KEY",
    )
    algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    expire_minutes: int = Field(default=1440, validation_alias="JWT_EXPIRE_MINUTES")


class S3Settings(BaseSettings):
    """Object storage (S3 / MinIO) configuration."""

    model_config = _SETTINGS_CONFIG

    endpoint: str = Field(default="", validation_alias="S3_ENDPOINT")
    secure: bool = Field(default=False, validation_alias="S3_SECURE")
    access_key: str = Field(default="", validation_alias="S3_ACCESS_KEY")
    secret_key: str = Field(default="", validation_alias="S3_SECRET_KEY")
    bucket_name: str = Field(
        default="boilerplate-uploads", validation_alias="S3_BUCKET_NAME"
    )


class LLMSettings(BaseSettings):
    """Self-hosted LLM configuration."""

    model_config = _SETTINGS_CONFIG

    api_base_url: str = Field(
        default="http://localhost:8000/v1", validation_alias="LLM_API_BASE_URL"
    )
    api_key: str = Field(default="dummy-key", validation_alias="LLM_API_KEY")
    model_name: str = Field(default="default", validation_alias="LLM_MODEL_NAME")
    temperature: float = Field(default=0.7, validation_alias="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2048, validation_alias="LLM_MAX_TOKENS")
    use_local_fallback: bool = Field(
        default=True, validation_alias="USE_LOCAL_FALLBACK"
    )


class EmbeddingSettings(BaseSettings):
    """Self-hosted Embedding configuration."""

    model_config = _SETTINGS_CONFIG

    api_base_url: str = Field(
        default="http://localhost:8000/v1", validation_alias="EMBEDDING_API_BASE_URL"
    )
    api_key: str = Field(default="dummy-key", validation_alias="EMBEDDING_API_KEY")
    model_name: str = Field(
        default="default-embed", validation_alias="EMBEDDING_MODEL_NAME"
    )
    dimension: int = Field(default=384, validation_alias="EMBEDDING_DIMENSION")
    use_local_fallback: bool = Field(
        default=True, validation_alias="USE_LOCAL_FALLBACK"
    )


class VectorStoreSettings(BaseSettings):
    """Vector database storage configuration (pgvector or ChromaDB)."""

    model_config = _SETTINGS_CONFIG

    store_type: str = Field(default="chroma", validation_alias="VECTOR_STORE_TYPE")
    chroma_persist_dir: str = Field(
        default="./data/storage/chroma", validation_alias="CHROMA_PERSIST_DIR"
    )
    chroma_collection_name: str = Field(
        default="viral_video_patterns", validation_alias="CHROMA_COLLECTION_NAME"
    )


# Cached Singleton Getters
@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache
def get_db_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()


@lru_cache
def get_s3_settings() -> S3Settings:
    return S3Settings()


@lru_cache
def get_llm_settings() -> LLMSettings:
    return LLMSettings()


@lru_cache
def get_embedding_settings() -> EmbeddingSettings:
    return EmbeddingSettings()


@lru_cache
def get_vector_store_settings() -> VectorStoreSettings:
    return VectorStoreSettings()


# Module-level instances for direct imports
app_settings = get_app_settings()
db_settings = get_db_settings()
auth_settings = get_auth_settings()
s3_settings = get_s3_settings()
llm_settings = get_llm_settings()
embedding_settings = get_embedding_settings()
vector_store_settings = get_vector_store_settings()

