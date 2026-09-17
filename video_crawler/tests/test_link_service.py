from collections.abc import AsyncIterator
from uuid import uuid4

import pytest

from video_crawler.domain import CrawlJobRequest, DiscoveredVideo, DiscoveryMethod, LeasedJob, Platform
from video_crawler.service import CrawlService


class Crawler:
    platform = Platform.FACEBOOK

    async def discover(self, request: CrawlJobRequest) -> AsyncIterator[DiscoveredVideo]:
        for index in range(3):
            yield DiscoveredVideo(
                platform=self.platform,
                platform_video_id=str(index),
                canonical_url=f"https://www.facebook.com/reel/{index}",
                caption="food",
            )


class Repository:
    def __init__(self) -> None:
        self.saved = []
        self.results = []

    async def find_video(self, *args: object) -> bool:
        return False

    async def save_video(self, job_id, video):
        self.saved.append(video)
        return uuid4()

    async def record_result(self, job_id, result, reason=None):
        self.results.append((result, reason))

    async def finish_job(self, job_id, failed=False):
        return None


@pytest.mark.asyncio
async def test_scheduled_service_saves_only_two_links_without_media() -> None:
    repository = Repository()
    request = CrawlJobRequest(
        (Platform.FACEBOOK,), DiscoveryMethod.KEYWORD, query="food",
        max_items_per_platform=10, max_new_links=2,
    )
    count = await CrawlService(repository=repository, crawlers=[Crawler()]).run_job(LeasedJob(uuid4(), request))

    assert count == 2
    assert [video.canonical_url for video in repository.saved] == [
        "https://www.facebook.com/reel/0", "https://www.facebook.com/reel/1"
    ]
    assert repository.saved[0].video_url == repository.saved[0].canonical_url


@pytest.mark.asyncio
async def test_retry_counts_links_saved_in_previous_attempt() -> None:
    repository = Repository()
    request = CrawlJobRequest(
        (Platform.FACEBOOK,), DiscoveryMethod.KEYWORD, query="food",
        max_items_per_platform=10, max_new_links=2,
    )
    job = LeasedJob(uuid4(), request, attempt_count=2, accepted_count=1)

    count = await CrawlService(repository=repository, crawlers=[Crawler()]).run_job(job)

    assert count == 2
    assert len(repository.saved) == 1
