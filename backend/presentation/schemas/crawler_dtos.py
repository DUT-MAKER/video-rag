"""Request DTOs for crawler administration."""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from video_crawler.domain import CrawlJobRequest, DiscoveryMethod, Platform


class CreateCrawlJobDTO(BaseModel):
    platforms: list[Platform] = Field(min_length=1)
    discovery_method: DiscoveryMethod = DiscoveryMethod.KEYWORD
    query: str = ""
    platform_queries: dict[Platform, str] = Field(default_factory=dict)
    creators: dict[Platform, str] = Field(default_factory=dict)
    source_urls: dict[Platform, str] = Field(default_factory=dict)
    max_items_per_platform: int = Field(default=20, ge=1, le=100)
    min_views: int | None = Field(default=None, ge=0)
    min_likes: int | None = Field(default=None, ge=0)
    min_comments: int | None = Field(default=None, ge=0)
    min_shares: int | None = Field(default=None, ge=0)
    published_after: datetime | None = None
    published_before: datetime | None = None
    max_scrolls: int = Field(default=8, ge=0, le=100)
    scroll_pause_seconds: float = Field(default=1.5, ge=0, le=30)

    @model_validator(mode="after")
    def validate_domain_request(self) -> "CreateCrawlJobDTO":
        self.to_domain()
        return self

    def to_domain(self) -> CrawlJobRequest:
        return CrawlJobRequest(
            platforms=tuple(self.platforms),
            discovery_method=self.discovery_method,
            query=self.query,
            platform_queries=self.platform_queries,
            creators=self.creators,
            source_urls=self.source_urls,
            max_items_per_platform=self.max_items_per_platform,
            min_views=self.min_views,
            min_likes=self.min_likes,
            min_comments=self.min_comments,
            min_shares=self.min_shares,
            published_after=self.published_after,
            published_before=self.published_before,
            max_scrolls=self.max_scrolls,
            scroll_pause_seconds=self.scroll_pause_seconds,
        )
