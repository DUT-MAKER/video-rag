"""Request DTOs for crawler administration and internal ingestion."""

from typing import Any

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
        )


class CrawlerRagRecordDTO(BaseModel):
    id: str
    caption: str = Field(min_length=1)
    hashtag: str = Field(min_length=1)
    transcript: str = Field(min_length=1)
    image_url: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    video_url: str = Field(min_length=1)
    platform: Platform
    platform_video_id: str = Field(min_length=1)
    canonical_url: str = Field(min_length=1)
    metrics: dict[str, Any] = Field(default_factory=dict)
    published_at: str = ""
    provenance: dict[str, Any] = Field(default_factory=dict)


class InternalCrawlerIngestDTO(BaseModel):
    record: CrawlerRagRecordDTO
