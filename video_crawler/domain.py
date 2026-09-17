"""Framework-free crawler domain types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from urllib.parse import urlparse
from uuid import UUID, uuid4


class Platform(StrEnum):
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


class DiscoveryMethod(StrEnum):
    KEYWORD = "keyword"
    HASHTAG = "hashtag"
    CREATOR = "creator"
    SOURCE_URL = "source_url"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True)
class CrawlJobRequest:
    platforms: tuple[Platform, ...]
    discovery_method: DiscoveryMethod
    query: str = ""
    platform_queries: dict[Platform, str] = field(default_factory=dict)
    creators: dict[Platform, str] = field(default_factory=dict)
    source_urls: dict[Platform, str] = field(default_factory=dict)
    max_items_per_platform: int = 20
    max_new_links: int | None = None
    min_views: int | None = None
    min_likes: int | None = None
    min_comments: int | None = None
    min_shares: int | None = None
    published_after: datetime | None = None
    published_before: datetime | None = None
    max_scrolls: int = 8
    scroll_pause_seconds: float = 1.5

    def __post_init__(self) -> None:
        if not self.platforms:
            raise ValueError("At least one platform is required")
        if not 1 <= self.max_items_per_platform <= 100:
            raise ValueError("max_items_per_platform must be between 1 and 100")
        if self.max_new_links is not None and not 1 <= self.max_new_links <= self.max_items_per_platform:
            raise ValueError("max_new_links must be between 1 and max_items_per_platform")
        if len(set(self.platforms)) != len(self.platforms):
            raise ValueError("Duplicate platforms are not allowed")
        for name in ("min_views", "min_likes", "min_comments", "min_shares"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.published_after and self.published_before and self.published_after > self.published_before:
            raise ValueError("published_after must be before published_before")
        if not 0 <= self.max_scrolls <= 100:
            raise ValueError("max_scrolls must be between 0 and 100")
        if not 0 <= self.scroll_pause_seconds <= 30:
            raise ValueError("scroll_pause_seconds must be between 0 and 30")
        for platform in self.platforms:
            if self.discovery_method is DiscoveryMethod.SOURCE_URL:
                if not self.source_urls.get(platform):
                    raise ValueError(f"Missing source URL for {platform.value}")
                _validate_source_url(platform, self.source_urls[platform])
            elif self.discovery_method is DiscoveryMethod.CREATOR:
                if not self.creators.get(platform):
                    raise ValueError(f"Missing creator for {platform.value}")
            elif not self.platform_queries.get(platform, self.query).strip():
                raise ValueError(f"Missing query for {platform.value}")

    def value_for(self, platform: Platform) -> str:
        if self.discovery_method is DiscoveryMethod.SOURCE_URL:
            return self.source_urls[platform]
        if self.discovery_method is DiscoveryMethod.CREATOR:
            return self.creators[platform]
        return self.platform_queries.get(platform, self.query)

    def to_dict(self) -> dict[str, Any]:
        return {
            "platforms": [item.value for item in self.platforms],
            "discovery_method": self.discovery_method.value,
            "query": self.query,
            "platform_queries": {key.value: value for key, value in self.platform_queries.items()},
            "creators": {key.value: value for key, value in self.creators.items()},
            "source_urls": {key.value: value for key, value in self.source_urls.items()},
            "max_items_per_platform": self.max_items_per_platform,
            "max_new_links": self.max_new_links,
            "min_views": self.min_views,
            "min_likes": self.min_likes,
            "min_comments": self.min_comments,
            "min_shares": self.min_shares,
            "published_after": self.published_after.isoformat() if self.published_after else None,
            "published_before": self.published_before.isoformat() if self.published_before else None,
            "max_scrolls": self.max_scrolls,
            "scroll_pause_seconds": self.scroll_pause_seconds,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CrawlJobRequest":
        return cls(
            platforms=tuple(Platform(item) for item in value["platforms"]),
            discovery_method=DiscoveryMethod(value["discovery_method"]),
            query=str(value.get("query") or ""),
            platform_queries={Platform(k): str(v) for k, v in value.get("platform_queries", {}).items()},
            creators={Platform(k): str(v) for k, v in value.get("creators", {}).items()},
            source_urls={Platform(k): str(v) for k, v in value.get("source_urls", {}).items()},
            max_items_per_platform=int(value.get("max_items_per_platform", 20)),
            max_new_links=_optional_int(value.get("max_new_links")),
            min_views=_optional_int(value.get("min_views")),
            min_likes=_optional_int(value.get("min_likes")),
            min_comments=_optional_int(value.get("min_comments")),
            min_shares=_optional_int(value.get("min_shares")),
            published_after=_optional_datetime(value.get("published_after")),
            published_before=_optional_datetime(value.get("published_before")),
            max_scrolls=int(value.get("max_scrolls", 8)),
            scroll_pause_seconds=float(value.get("scroll_pause_seconds", 1.5)),
        )


@dataclass
class DiscoveredVideo:
    platform: Platform
    platform_video_id: str
    canonical_url: str
    caption: str
    hashtags: list[str] = field(default_factory=list)
    thumbnail_url: str = ""
    metrics: dict[str, int | float] = field(default_factory=dict)
    published_at: datetime | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class MediaArtifact:
    video_path: str
    thumbnail_path: str | None
    duration_seconds: float | None
    work_dir: str
    metrics: dict[str, int | float] = field(default_factory=dict)


@dataclass
class CrawledVideo:
    platform: Platform
    platform_video_id: str
    canonical_url: str
    caption: str
    hashtag: str
    image_url: str
    video_url: str
    metrics: dict[str, int | float] = field(default_factory=dict)
    published_at: datetime | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    quality_warnings: list[str] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

@dataclass
class LeasedJob:
    id: UUID
    request: CrawlJobRequest
    attempt_count: int = 1
    accepted_count: int = 0


def utc_now() -> datetime:
    return datetime.now(UTC)


def _validate_source_url(platform: Platform, value: str) -> None:
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    allowed = {
        Platform.FACEBOOK: ("facebook.com", "fb.watch"),
        Platform.TIKTOK: ("tiktok.com",),
        Platform.YOUTUBE: ("youtube.com", "youtu.be"),
    }[platform]
    if parsed.scheme not in {"http", "https"} or not any(
        host == domain or host.endswith(f".{domain}") for domain in allowed
    ):
        raise ValueError(f"Invalid {platform.value} source URL")


def _optional_int(value: Any) -> int | None:
    return None if value in (None, "") else int(value)


def _optional_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
