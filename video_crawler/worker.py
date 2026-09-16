"""One scheduled crawler worker per platform."""

from __future__ import annotations

import asyncio
import logging
import os
import socket
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler

from backend.di.database import async_session_factory
from video_crawler.config import get_crawler_settings
from video_crawler.crawlers import FacebookCrawler, TikTokCrawler, YouTubeCrawler
from video_crawler.domain import Platform
from video_crawler.infrastructure.browser import BrowserContextFactory
from video_crawler.infrastructure.repository import CrawlerRepository
from video_crawler.schedule import ScheduleConfig, due_slot
from video_crawler.service import CrawlService

LOGGER = logging.getLogger(__name__)
FATAL_CODES = {"AUTH_REQUIRED", "CHALLENGE_REQUIRED", "ACCESS_DENIED", "RATE_LIMITED"}


def should_retry(error: Exception, attempt: int, max_attempts: int) -> bool:
    code = str(error).split(":", 1)[0].strip().upper()
    return code not in FATAL_CODES and attempt < max_attempts


def retry_delay(base_seconds: int, attempt: int) -> int:
    return base_seconds * (2 ** (attempt - 1))


async def run_worker() -> None:
    settings = get_crawler_settings()
    platform = Platform(os.environ["CRAWLER_PLATFORM"])
    repository = CrawlerRepository(async_session_factory)
    browser = BrowserContextFactory(settings)
    service = CrawlService(
        repository=repository,
        crawlers=[YouTubeCrawler(browser), TikTokCrawler(browser), FacebookCrawler(browser)],
    )
    owner = f"{socket.gethostname()}:{platform.value}:{os.getpid()}"
    consecutive_errors = 0
    last_scheduled_key: str | None = None
    LOGGER.info("Worker started: platform=%s owner=%s", platform.value, owner)
    while True:
        try:
            config = ScheduleConfig.from_file(settings.topics_file)
            slot = due_slot(config, platform, datetime.now(UTC))
            if slot and slot.key != last_scheduled_key:
                job_id = await repository.create_scheduled_job(slot)
                last_scheduled_key = slot.key
                if job_id:
                    LOGGER.info("Scheduled job: platform=%s keyword=%r slot=%s job_id=%s", platform.value, slot.keyword, slot.key, job_id)
            job = await repository.lease_job(owner, platform=platform)
            if job:
                LOGGER.info("Job started: job_id=%s attempt=%d", job.id, job.attempt_count)
                try:
                    accepted = await service.run_job(job)
                    if accepted:
                        LOGGER.info("Job completed: job_id=%s links=%d", job.id, accepted)
                    else:
                        LOGGER.warning("Job finished without new links: job_id=%s", job.id)
                except Exception as error:
                    detail = f"{type(error).__name__}: {error}"
                    if should_retry(error, job.attempt_count, config.max_attempts):
                        delay = retry_delay(config.retry_delay_seconds, job.attempt_count)
                        await repository.retry_job(job.id, detail, delay)
                        LOGGER.warning("Job retry queued: job_id=%s delay=%ds reason=%s", job.id, delay, detail)
                    else:
                        await repository.fail_job(job.id, detail)
                        LOGGER.error("Job stopped: job_id=%s reason=%s", job.id, detail)
            consecutive_errors = 0
            await asyncio.sleep(settings.worker_poll_seconds)
        except Exception:
            consecutive_errors += 1
            LOGGER.exception("Worker loop error: platform=%s consecutive=%d", platform.value, consecutive_errors)
            await asyncio.sleep(min(300, 2 ** min(consecutive_errors, 8)))


def main() -> None:
    settings = get_crawler_settings()
    platform = Platform(os.environ["CRAWLER_PLATFORM"])
    log_dir = settings.work_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(log_dir / f"{platform.value}.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"),
        ],
    )
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
