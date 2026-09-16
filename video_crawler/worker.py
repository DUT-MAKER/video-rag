"""Dedicated crawler worker process entrypoint."""

from __future__ import annotations

import asyncio
import logging
import socket

from backend.di.database import async_session_factory
from core.config import s3_settings
from video_crawler.config import get_crawler_settings
from video_crawler.crawlers import FacebookCrawler, TikTokCrawler, YouTubeCrawler
from video_crawler.infrastructure.browser import BrowserContextFactory
from video_crawler.infrastructure.media import YtDlpMediaResolver
from video_crawler.infrastructure.repository import CrawlerRepository
from video_crawler.infrastructure.storage import S3CrawlerStorage
from video_crawler.service import CrawlService


async def run_worker() -> None:
    settings = get_crawler_settings()
    repository = CrawlerRepository(async_session_factory)
    browser = BrowserContextFactory(settings)
    service = CrawlService(
        repository=repository,
        crawlers=[YouTubeCrawler(browser), TikTokCrawler(browser), FacebookCrawler(browser)],
        media=YtDlpMediaResolver(settings),
        storage=S3CrawlerStorage(s3_settings, settings),
    )
    owner = f"{socket.gethostname()}:{id(service)}"
    while True:
        job = await repository.lease_job(owner)
        if job:
            await service.run_job(job)
        else:
            await asyncio.sleep(settings.worker_poll_seconds)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
