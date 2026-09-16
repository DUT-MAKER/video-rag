from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest

from video_crawler.domain import (
    CrawlJobRequest,
    CrawledVideo,
    DiscoveredVideo,
    DiscoveryMethod,
    LeasedJob,
    MediaArtifact,
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


class FakeMedia:
    async def resolve(self, video: DiscoveredVideo) -> MediaArtifact:
        return MediaArtifact("video.mp4", "thumb.jpg", [], 30.0, "work")

    async def cleanup(self, artifact: MediaArtifact) -> None:
        return None


class FakeTranscript:
    async def transcribe(self, artifact: MediaArtifact) -> str:
        return "Start with a clear promise and deliver the result quickly."


class FakeStorage:
    async def store(self, video: DiscoveredVideo, artifact: MediaArtifact) -> tuple[str, str]:
        return "https://minio/video.mp4", "https://minio/thumb.jpg"


class FakeSummary:
    async def summarize(self, caption: str, transcript: str) -> str:
        return "The video explains three retention techniques."


class FlakyIngestor:
    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.calls = 0

    async def ingest(self, video: CrawledVideo) -> None:
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError("temporary backend outage")


class FakeRepository:
    def __init__(self) -> None:
        self.saved: tuple[UUID, CrawledVideo] | None = None
        self.video_id = uuid4()
        self.results: list[tuple[str, str | None]] = []
        self.indexed = False
        self.attempts = 0

    async def create_job(self, request: CrawlJobRequest) -> UUID:
        return uuid4()

    async def lease_job(self, owner: str) -> None:
        return None

    async def find_video(self, platform: Platform, platform_video_id: str, canonical_url: str) -> bool:
        return False

    async def save_video(self, job_id: UUID, video: CrawledVideo) -> UUID:
        self.saved = (job_id, video)
        return self.video_id

    async def mark_indexed(self, video_id: UUID) -> None:
        self.indexed = True
        self.attempts += 1

    async def mark_ingest_failed(self, video_id: UUID, detail: str) -> None:
        self.attempts += 1

    async def pending_ingest(self, max_attempts: int, limit: int = 20) -> list[tuple[UUID, UUID, CrawledVideo]]:
        if self.saved and not self.indexed and self.attempts < max_attempts:
            return [(self.saved[0], self.video_id, self.saved[1])]
        return []

    async def record_result(self, job_id: UUID, result: str, reason: str | None = None) -> None:
        self.results.append((result, reason))

    async def finish_job(self, job_id: UUID, failed: bool = False) -> None:
        return None

    async def fail_job(self, job_id: UUID, detail: str) -> None:
        return None


def service(repository: FakeRepository, ingestor: FlakyIngestor) -> CrawlService:
    return CrawlService(
        repository=repository,
        crawlers=[FakeCrawler()],
        media=FakeMedia(),
        transcript=FakeTranscript(),
        storage=FakeStorage(),
        summarizer=FakeSummary(),
        ingestor=ingestor,
        max_ingest_attempts=3,
    )


@pytest.mark.asyncio
async def test_complete_record_is_saved_and_ingested() -> None:
    repository = FakeRepository()
    ingestor = FlakyIngestor()
    request = CrawlJobRequest((Platform.YOUTUBE,), DiscoveryMethod.KEYWORD, query="retention")
    await service(repository, ingestor).run_job(LeasedJob(uuid4(), request))
    assert repository.saved is not None
    assert repository.indexed is True
    assert ingestor.calls == 1


@pytest.mark.asyncio
async def test_ingest_retry_uses_saved_record_without_recrawling() -> None:
    repository = FakeRepository()
    ingestor = FlakyIngestor(failures=1)
    crawler_service = service(repository, ingestor)
    request = CrawlJobRequest((Platform.YOUTUBE,), DiscoveryMethod.KEYWORD, query="retention")
    await crawler_service.run_job(LeasedJob(uuid4(), request))
    assert repository.saved is not None
    assert repository.indexed is False
    await crawler_service.retry_pending_ingest()
    assert repository.indexed is True
    assert ingestor.calls == 2
