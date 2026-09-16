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
    topics_file: Path = Field(
        default=ROOT_DIR / "video_crawler" / "topics.json",
        validation_alias="CRAWLER_TOPICS_FILE",
    )
    def session_file(self, platform: str) -> Path:
        return self.session_dir / f"{platform}.json"

    def browser_profile_dir(self, platform: str) -> Path:
        return self.session_dir.parent / "profiles" / platform


@lru_cache
def get_crawler_settings() -> CrawlerSettings:
    return CrawlerSettings()
