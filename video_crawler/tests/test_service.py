from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest

from video_crawler.domain import (
    CrawlJobRequest,
    CrawledVideo,
    DiscoveredVideo,
    DiscoveryMethod,
    LeasedJob,
    Platform,
)
from video_crawler.service import CrawlService


class FakeCrawler:
    platform = Platform.YOUTUBE

    async def discover(self, request: CrawlJobRequest) -> AsyncIterator[DiscoveredVideo]:
        yield DiscoveredVideo(
            platform=self.platform,
            platform_video_id="abc123",
            canonical_url="https://youtube.com/watch?v=abc123",
            caption="Three ways to improve retention",
            hashtags=["retention"],
        )


class FakeRepository:
    def __init__(self) -> None:
        self.saved: tuple[UUID, CrawledVideo] | None = None
        self.video_id = uuid4()
        self.results: list[tuple[str, str | None]] = []

    async def create_job(self, request: CrawlJobRequest) -> UUID:
        return uuid4()

    async def lease_job(self, owner: str) -> None:
        return None

    async def find_video(self, platform: Platform, platform_video_id: str, canonical_url: str) -> bool:
        return False

    async def save_video(self, job_id: UUID, video: CrawledVideo) -> UUID:
        self.saved = (job_id, video)
        return self.video_id

    async def record_result(self, job_id: UUID, result: str, reason: str | None = None) -> None:
        self.results.append((result, reason))

    async def finish_job(self, job_id: UUID, failed: bool = False) -> None:
        return None

    async def fail_job(self, job_id: UUID, detail: str) -> None:
        return None


def service(repository: FakeRepository) -> CrawlService:
    return CrawlService(
        repository=repository,
        crawlers=[FakeCrawler()],
    )


@pytest.mark.asyncio
async def test_complete_record_saves_source_url_without_download() -> None:
    repository = FakeRepository()
    request = CrawlJobRequest((Platform.YOUTUBE,), DiscoveryMethod.KEYWORD, query="retention")
    await service(repository).run_job(LeasedJob(uuid4(), request))
    assert repository.saved is not None
    saved = repository.saved[1]
    assert saved.video_url == saved.canonical_url
    assert saved.image_url == ""
    assert saved.metrics == {}
    assert ("accepted", None) in repository.results
