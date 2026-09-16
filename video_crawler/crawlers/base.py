"""Shared implementation for bounded browser discovery."""

from __future__ import annotations

from collections.abc import AsyncIterator
from urllib.parse import quote_plus

from playwright.async_api import Page

from video_crawler.domain import CrawlJobRequest, DiscoveredVideo, Platform
from video_crawler.infrastructure.browser import BrowserContextFactory, assert_page_access


class BrowserPlatformCrawler:
    platform: Platform

    def __init__(self, browser: BrowserContextFactory) -> None:
        self.browser = browser

    def build_url(self, request: CrawlJobRequest) -> str:
        raise NotImplementedError

    async def parse(self, page: Page) -> list[DiscoveredVideo]:
        raise NotImplementedError

    async def discover(self, request: CrawlJobRequest) -> AsyncIterator[DiscoveredVideo]:
        async with self.browser.open(self.platform) as context:
            page = await context.new_page()
            response = await page.goto(self.build_url(request), wait_until="domcontentloaded")
            if response and response.status == 429:
                raise RuntimeError("RATE_LIMITED: HTTP 429")
            if response and response.status in {401, 403}:
                raise RuntimeError(f"ACCESS_DENIED: HTTP {response.status}")
            await assert_page_access(page)
            records = await self.parse(page)
            if not records:
                raise RuntimeError("PARSER_BROKEN: no video records found")
            for record in records[: request.max_items_per_platform]:
                yield record


def encoded(value: str) -> str:
    return quote_plus(value)
