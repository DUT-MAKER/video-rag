"""Application service for discovering and deduplicating source video links."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from .domain import CrawledVideo, DiscoveredVideo, LeasedJob
from .ports import CrawlerRepositoryPort, PlatformCrawler

LOGGER = logging.getLogger(__name__)


class CrawlService:
    def __init__(self, repository: CrawlerRepositoryPort, crawlers: list[PlatformCrawler]) -> None:
        self.repository = repository
        self.crawlers = {crawler.platform: crawler for crawler in crawlers}

    async def run_job(self, job: LeasedJob) -> int:
        limit = job.request.max_new_links or job.request.max_items_per_platform
        accepted_total = job.accepted_count
        for platform in job.request.platforms:
            accepted_for_platform = job.accepted_count if len(job.request.platforms) == 1 else 0
            if accepted_for_platform >= limit:
                continue
            try:
                async for discovered in self.crawlers[platform].discover(job.request):
                    await self.repository.record_result(job.id, "discovered")
                    if await self._save_link(job, discovered):
                        accepted_for_platform += 1
                        accepted_total += 1
                    if accepted_for_platform >= limit:
                        break
            except Exception:
                LOGGER.exception("Crawler failed: job_id=%s platform=%s", job.id, platform.value)
                raise
        await self.repository.finish_job(job.id)
        return accepted_total

    async def _save_link(self, job: LeasedJob, discovered: DiscoveredVideo) -> bool:
        if not discovered.platform_video_id or not discovered.canonical_url.startswith("https://"):
            await self.repository.record_result(job.id, "rejected", "invalid_video_url")
            return False
        if "ui_contaminated" in discovered.warnings:
            await self.repository.record_result(job.id, "rejected", "ui_contaminated")
            return False
        if await self.repository.find_video(
            discovered.platform, discovered.platform_video_id, discovered.canonical_url
        ):
            await self.repository.record_result(job.id, "rejected", "duplicate")
            return False
        video = CrawledVideo(
            platform=discovered.platform,
            platform_video_id=discovered.platform_video_id,
            canonical_url=discovered.canonical_url,
            caption=discovered.caption.strip(),
            hashtag=" ".join(f"#{item.lstrip('#')}" for item in discovered.hashtags),
            image_url=discovered.thumbnail_url,
            video_url=discovered.canonical_url,
            metrics=discovered.metrics,
            published_at=discovered.published_at,
            quality_warnings=discovered.warnings,
            provenance={
                "crawler": f"video-crawler-{discovered.platform.value}",
                "schema_version": "3.0",
                "discovery_method": job.request.discovery_method.value,
                "collected_at": datetime.now(UTC).isoformat(),
                "query": job.request.value_for(discovered.platform),
            },
        )
        if await self.repository.save_video(job.id, video) is None:
            await self.repository.record_result(job.id, "rejected", "duplicate")
            return False
        await self.repository.record_result(job.id, "accepted")
        return True
