"""Request DTOs for crawler administration."""

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
