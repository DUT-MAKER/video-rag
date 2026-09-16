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
            records: dict[str, DiscoveredVideo] = {}
            for scroll_number in range(request.max_scrolls + 1):
                for record in await self.parse(page):
                    records[record.canonical_url] = record
                if len(records) >= request.max_items_per_platform or scroll_number == request.max_scrolls:
                    break
                await page.mouse.wheel(0, 1000)
                await page.wait_for_timeout(int(request.scroll_pause_seconds * 1000))
            if not records:
                raise RuntimeError("PARSER_BROKEN: no video records found")
            for record in list(records.values())[: request.max_items_per_platform]:
                yield record


def encoded(value: str) -> str:
    return quote_plus(value)
