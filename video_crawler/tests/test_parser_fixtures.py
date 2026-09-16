import json
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


def test_tiktok_hydration_parser_extracts_url_and_metrics() -> None:
    payload = json.dumps(
        {
            "item": {
                "id": "7681809255510461717",
                "author": {"uniqueId": "creator"},
                "desc": "Example #viral",
                "stats": {
                    "playCount": 1000,
                    "diggCount": 90,
                    "commentCount": 12,
                    "shareCount": 7,
                },
                "video": {"cover": "https://img.example/cover.jpg"},
                "createTime": "1700000000",
            }
        }
    )

    records = TikTokCrawler._parse_hydration_payloads([payload])

    assert len(records) == 1
    assert records[0].canonical_url == (
        "https://www.tiktok.com/@creator/video/7681809255510461717"
    )
    assert records[0].hashtags == ["viral"]
    assert records[0].metrics == {
        "view_count": 1000,
        "like_count": 90,
        "comment_count": 12,
        "share_count": 7,
    }
