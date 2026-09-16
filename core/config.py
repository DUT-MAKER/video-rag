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
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:3002,http://127.0.0.1:3002",
        validation_alias="CORS_ORIGINS",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """Parses comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


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
    bucket_name: str = Field(default="boilerplate-uploads", validation_alias="S3_BUCKET_NAME")


class LLMSettings(BaseSettings):
    """Self-hosted LLM configuration (DUT AI Gemma 4)."""

    model_config = _SETTINGS_CONFIG

    api_base_url: str = Field(default="https://llm2.dutai.site/v1", validation_alias="LLM_API_BASE_URL")
    api_key: str = Field(default="", validation_alias="LLM_API_KEY")
    model_name: str = Field(default="ggml-org/gemma-4-e4b-it-GGUF:Q4_0", validation_alias="LLM_MODEL_NAME")
    temperature: float = Field(default=0.7, validation_alias="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2048, validation_alias="LLM_MAX_TOKENS")


class EmbeddingSettings(BaseSettings):
    """Text Embedding configuration (DUT AI / BAAI/bge-m3 default)."""

    model_config = _SETTINGS_CONFIG

    api_base_url: str = Field(default="https://textembedding.dutai.io.vn/v1", validation_alias="EMBEDDING_API_BASE_URL")
    api_key: str = Field(default="dutaiclb", validation_alias="EMBEDDING_API_KEY")
    model_name: str = Field(default="BAAI/bge-m3", validation_alias="EMBEDDING_MODEL_NAME")
    dimension: int = Field(default=1024, validation_alias="EMBEDDING_DIMENSION")


class RerankSettings(BaseSettings):
    """Text Reranker configuration (DUT AI / BAAI/bge-reranker-v2-m3)."""

    model_config = _SETTINGS_CONFIG

    api_base_url: str = Field(default="https://textembedding.dutai.io.vn", validation_alias="RERANK_API_BASE_URL")
    api_key: str = Field(default="dutaiclb", validation_alias="RERANK_API_KEY")
    model_name: str = Field(default="BAAI/bge-reranker-v2-m3", validation_alias="RERANK_MODEL_NAME")
    enabled: bool = Field(default=True, validation_alias="RERANK_ENABLED")
    candidate_k: int = Field(default=15, validation_alias="RERANK_CANDIDATE_K")
    top_n: int = Field(default=3, validation_alias="RERANK_TOP_N")
    timeout: float = Field(default=15.0, validation_alias="RERANK_TIMEOUT")


class VectorStoreSettings(BaseSettings):
    """Vector database storage configuration (PostgreSQL pgvector)."""

    model_config = _SETTINGS_CONFIG

    table_name: str = Field(default="viral_video_embeddings", validation_alias="PGVECTOR_TABLE_NAME")
    store_type: str = Field(default="pgvector", validation_alias="VECTOR_STORE_TYPE")


class TranscriberSettings(BaseSettings):
    """Speech-to-text and speaker diarization configuration."""

    model_config = _SETTINGS_CONFIG

    whisper_model: str = Field(
        default="large-v3-turbo", validation_alias="WHISPER_MODEL"
    )
    whisper_device: str = Field(default="cuda", validation_alias="WHISPER_DEVICE")
    whisper_compute_type: str = Field(
        default="float16", validation_alias="WHISPER_COMPUTE_TYPE"
    )
    whisper_batch_size: int = Field(default=16, validation_alias="WHISPER_BATCH_SIZE")
    hf_token: str = Field(default="", validation_alias="HF_TOKEN")
    default_language: str = Field(
        default="vi", validation_alias="STT_DEFAULT_LANGUAGE"
    )
    enable_diarization: bool = Field(
        default=True, validation_alias="ENABLE_DIARIZATION"
    )
    diarization_device: str = Field(
        default="cpu", validation_alias="DIARIZATION_DEVICE"
    )
    bento_stt_url: str = Field(
        default="http://localhost:3001", validation_alias="BENTO_STT_URL"
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
def get_rerank_settings() -> RerankSettings:
    return RerankSettings()


@lru_cache
def get_vector_store_settings() -> VectorStoreSettings:
    return VectorStoreSettings()


@lru_cache
def get_transcriber_settings() -> TranscriberSettings:
    return TranscriberSettings()


# Module-level instances for direct imports
app_settings = get_app_settings()
db_settings = get_db_settings()
auth_settings = get_auth_settings()
s3_settings = get_s3_settings()
llm_settings = get_llm_settings()
embedding_settings = get_embedding_settings()
rerank_settings = get_rerank_settings()
vector_store_settings = get_vector_store_settings()
transcriber_settings = get_transcriber_settings()


