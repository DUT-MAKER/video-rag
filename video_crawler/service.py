"""Application service orchestrating discovery, download and object storage."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from .domain import CrawledVideo, DiscoveredVideo, LeasedJob
from .ports import (
    CrawlerRepositoryPort,
    MediaResolver,
    ObjectStorage,
    PlatformCrawler,
)
from .quality import check_video_quality

LOGGER = logging.getLogger(__name__)


class CrawlService:
    def __init__(
        self,
        repository: CrawlerRepositoryPort,
        crawlers: list[PlatformCrawler],
        media: MediaResolver,
        storage: ObjectStorage,
    ) -> None:
        self.repository = repository
        self.crawlers = {crawler.platform: crawler for crawler in crawlers}
        self.media = media
        self.storage = storage

    async def run_job(self, job: LeasedJob) -> None:
        try:
            for platform in job.request.platforms:
                crawler = self.crawlers[platform]
                try:
                    async for discovered in crawler.discover(job.request):
                        await self.repository.record_result(job.id, "discovered")
                        await self._process_video(job, discovered)
                except Exception as error:  # isolate platform failure
                    reason = _failure_code(error)
                    LOGGER.warning("Crawler platform failed: platform=%s reason=%s", platform.value, reason)
                    await self.repository.record_result(job.id, "rejected", reason)
            await self.repository.finish_job(job.id)
        except Exception as error:
            LOGGER.exception("Crawler job failed: job_id=%s", job.id)
            await self.repository.fail_job(job.id, str(error))

    async def _process_video(self, job: LeasedJob, discovered: DiscoveredVideo) -> None:
        if not discovered.platform_video_id or not discovered.caption.strip():
            await self.repository.record_result(job.id, "rejected", "metadata_incomplete")
            return
        if "ui_contaminated" in discovered.warnings:
            await self.repository.record_result(job.id, "rejected", "ui_contaminated")
            return
        if await self.repository.find_video(
            discovered.platform, discovered.platform_video_id, discovered.canonical_url
        ):
            await self.repository.record_result(job.id, "rejected", "duplicate")
            return

        artifact = None
        try:
            artifact = await self.media.resolve(discovered)
            video_url, image_url = await self.storage.store(discovered, artifact)
            hashtags = discovered.hashtags or [discovered.platform.value]
            video = CrawledVideo(
                platform=discovered.platform,
                platform_video_id=discovered.platform_video_id,
                canonical_url=discovered.canonical_url,
                caption=discovered.caption.strip(),
                hashtag=" ".join(f"#{item.lstrip('#')}" for item in hashtags),
                image_url=image_url,
                video_url=video_url,
                metrics={**discovered.metrics, **artifact.metrics},
                published_at=discovered.published_at,
                quality_warnings=discovered.warnings,
                provenance={
                    "crawler": f"video-crawler-{discovered.platform.value}",
                    "schema_version": "2.0",
                    "discovery_method": job.request.discovery_method.value,
                    "collected_at": datetime.now(UTC).isoformat(),
                    "query": job.request.value_for(discovered.platform),
                    "duration_seconds": artifact.duration_seconds,
                },
            )
            quality = check_video_quality(video)
            if not quality.accepted:
                await self.repository.record_result(
                    job.id, "rejected", "+".join(quality.reasons)
                )
                return
            await self.repository.save_video(job.id, video)
            await self.repository.record_result(job.id, "accepted")
        except Exception as error:
            reason = _failure_code(error)
            LOGGER.warning(
                "Video processing failed: platform=%s video_id=%s reason=%s",
                discovered.platform.value,
                discovered.platform_video_id,
                reason,
            )
            await self.repository.record_result(job.id, "rejected", reason)
        finally:
            if artifact:
                await self.media.cleanup(artifact)


def _failure_code(error: Exception) -> str:
    prefix = str(error).split(":", 1)[0].strip().lower()
    safe = {
        "auth_required",
        "challenge_required",
        "rate_limited",
        "access_denied",
        "parser_broken",
        "media_download_failed",
        "thumbnail_missing",
    }
    return prefix if prefix in safe else type(error).__name__.lower()
