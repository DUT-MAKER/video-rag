from datetime import UTC, datetime
from pathlib import Path

import pytest
from playwright.async_api import async_playwright

from video_crawler.crawlers.facebook import FacebookCrawler, _extract_caption, matches_search_filters
from video_crawler.domain import CrawlJobRequest, DiscoveredVideo, DiscoveryMethod, Platform


FIXTURES = Path(__file__).with_name("fixtures")


def _video(**overrides: object) -> DiscoveredVideo:
    values: dict[str, object] = {
        "platform": Platform.FACEBOOK,
        "platform_video_id": "987654",
        "canonical_url": "https://www.facebook.com/reel/987654",
        "caption": "How to build a better hook #creator",
        "metrics": {"views": 1_500_000, "likes": 25_000, "comments": 1_200, "shares": 800},
        "published_at": datetime(2025, 6, 1, tzinfo=UTC),
    }
    values.update(overrides)
    return DiscoveredVideo(**values)


def test_facebook_build_url_preserves_user_search_intent() -> None:
    crawler = FacebookCrawler(browser=None)  # type: ignore[arg-type]

    keyword = CrawlJobRequest((Platform.FACEBOOK,), DiscoveryMethod.KEYWORD, query="street food vietnam")
    hashtag = CrawlJobRequest((Platform.FACEBOOK,), DiscoveryMethod.HASHTAG, query="#streetfood")
    creator = CrawlJobRequest((Platform.FACEBOOK,), DiscoveryMethod.CREATOR, creators={Platform.FACEBOOK: "natgeo"})
    source = CrawlJobRequest(
        (Platform.FACEBOOK,),
        DiscoveryMethod.SOURCE_URL,
        source_urls={Platform.FACEBOOK: "https://www.facebook.com/reel/987654"},
    )

    assert "search/videos" in crawler.build_url(keyword)
    assert "street+food+vietnam" in crawler.build_url(keyword)
    assert "streetfood" in crawler.build_url(hashtag)
    assert crawler.build_url(creator).endswith("/natgeo/reels")
    assert crawler.build_url(source) == "https://www.facebook.com/reel/987654"


def test_search_filters_require_all_configured_viral_criteria() -> None:
    request = CrawlJobRequest(
        (Platform.FACEBOOK,),
        DiscoveryMethod.KEYWORD,
        query="street food",
        min_views=1_000_000,
        min_likes=20_000,
        min_comments=1_000,
        min_shares=500,
        published_after=datetime(2025, 1, 1, tzinfo=UTC),
        published_before=datetime(2025, 12, 31, tzinfo=UTC),
    )

    assert matches_search_filters(_video(), request)
    assert not matches_search_filters(_video(metrics={"views": 999_999}), request)
    assert not matches_search_filters(_video(published_at=datetime(2024, 12, 31, tzinfo=UTC)), request)
    assert not matches_search_filters(_video(published_at=None), request)


def test_search_filters_do_not_invent_unknown_metrics() -> None:
    request = CrawlJobRequest(
        (Platform.FACEBOOK,),
        DiscoveryMethod.KEYWORD,
        query="street food",
        min_views=1,
    )

    assert not matches_search_filters(_video(metrics={}), request)


def test_search_criteria_survive_job_persistence_round_trip() -> None:
    request = CrawlJobRequest(
        (Platform.FACEBOOK,),
        DiscoveryMethod.HASHTAG,
        query="#streetfood",
        min_views=100_000,
        min_likes=5_000,
        published_after=datetime(2025, 1, 1, tzinfo=UTC),
        max_scrolls=12,
        scroll_pause_seconds=2.0,
    )

    restored = CrawlJobRequest.from_dict(request.to_dict())

    assert restored == request


def test_caption_keeps_user_text_when_metrics_share_the_same_line() -> None:
    caption, warnings = _extract_caption("A strong opening hook #viral · 1.5M views · 25K reactions")

    assert caption == "A strong opening hook #viral"
    assert warnings == []


@pytest.mark.asyncio
async def test_facebook_parser_extracts_visible_metrics_and_published_at() -> None:
    crawler = FacebookCrawler(browser=None)  # type: ignore[arg-type]
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.set_content((FIXTURES / "facebook.html").read_text(encoding="utf-8"))
        records = await crawler.parse(page)
        await browser.close()

    assert records[0].metrics == {
        "views": 1_500_000,
        "likes": 25_000,
        "comments": 1_200,
        "shares": 800,
    }
    assert records[0].published_at == datetime(2025, 6, 1, 12, tzinfo=UTC)
