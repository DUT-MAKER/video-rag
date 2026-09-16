"""Crawler configuration sourced from the shared project environment."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class CrawlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    worker_poll_seconds: float = Field(
        default=2.0, validation_alias="CRAWLER_WORKER_POLL_SECONDS"
    )
    browser_headless: bool = Field(
        default=True, validation_alias="CRAWLER_BROWSER_HEADLESS"
    )
    session_dir: Path = Field(
        default=ROOT_DIR / "video_crawler" / "var" / "secrets" / "sessions",
        validation_alias="CRAWLER_SESSION_DIR",
    )
    work_dir: Path = Field(
        default=ROOT_DIR / "data" / "crawler-work",
        validation_alias="CRAWLER_WORK_DIR",
    )
    minio_prefix: str = Field(
        default="video-crawler", validation_alias="CRAWLER_MINIO_PREFIX"
    )
    ingest_url: str = Field(
        default="http://api:8000/api/v1/internal/crawler/ingest",
        validation_alias="CRAWLER_INGEST_URL",
    )
    internal_token: str = Field(default="", validation_alias="CRAWLER_INTERNAL_TOKEN")
    whisper_model: str = Field(default="small", validation_alias="CRAWLER_WHISPER_MODEL")
    whisper_device: str = Field(default="cpu", validation_alias="CRAWLER_WHISPER_DEVICE")
    whisper_compute_type: str = Field(
        default="int8", validation_alias="CRAWLER_WHISPER_COMPUTE_TYPE"
    )
    max_ingest_attempts: int = Field(
        default=3, validation_alias="CRAWLER_MAX_INGEST_ATTEMPTS"
    )

    def session_file(self, platform: str) -> Path:
        return self.session_dir / f"{platform}.json"


@lru_cache
def get_crawler_settings() -> CrawlerSettings:
    return CrawlerSettings()
