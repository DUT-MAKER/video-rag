from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from video_crawler.config import CrawlerSettings
from video_crawler.crawlers import FacebookCrawler, TikTokCrawler, YouTubeCrawler
from video_crawler.infrastructure.browser import BrowserContextFactory

FIXTURES = Path(__file__).with_name("fixtures")


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("crawler_type", "fixture", "expected_id"),
    [
        (YouTubeCrawler, "youtube.html", "abc123"),
        (TikTokCrawler, "tiktok.html", "123456"),
        (FacebookCrawler, "facebook.html", "987654"),
    ],
)
async def test_platform_parser_fixture(crawler_type, fixture: str, expected_id: str, tmp_path: Path) -> None:
    settings = CrawlerSettings(
        CRAWLER_SESSION_DIR=tmp_path / "sessions",
        CRAWLER_WORK_DIR=tmp_path / "work",
    )
    crawler = crawler_type(BrowserContextFactory(settings))
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.set_content((FIXTURES / fixture).read_text(encoding="utf-8"))
        records = await crawler.parse(page)
        await browser.close()
    assert records[0].platform_video_id == expected_id
