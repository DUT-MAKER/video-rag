"""Facebook discovery through the operator's browser search session."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from datetime import UTC, datetime

from playwright.async_api import Page

from video_crawler.crawlers.base import BrowserPlatformCrawler, encoded
from video_crawler.domain import CrawlJobRequest, DiscoveredVideo, DiscoveryMethod, Platform
from video_crawler.infrastructure.browser import assert_page_access, canonical_url, tail_id


class FacebookCrawler(BrowserPlatformCrawler):
    platform = Platform.FACEBOOK

    def build_url(self, request: CrawlJobRequest) -> str:
        value = request.value_for(self.platform).strip()
        if request.discovery_method is DiscoveryMethod.SOURCE_URL:
            return value
        if request.discovery_method is DiscoveryMethod.CREATOR:
            return f"https://www.facebook.com/{encoded(value.lstrip('@'))}/reels"
        return f"https://www.facebook.com/search/videos?q={encoded(value.lstrip('#'))}"

    async def discover(self, request: CrawlJobRequest) -> AsyncIterator[DiscoveredVideo]:
        """Scroll rendered search results and yield only records matching the request."""
        async with self.browser.open(self.platform) as context:
            page = await context.new_page()
            response = await page.goto(self.build_url(request), wait_until="domcontentloaded")
            if response and response.status == 429:
                raise RuntimeError("RATE_LIMITED: HTTP 429")
            if response and response.status in {401, 403}:
                raise RuntimeError(f"ACCESS_DENIED: HTTP {response.status}")
            await assert_page_access(page)

            records: dict[str, DiscoveredVideo] = {}
            previous_height = 0
            stagnant_scrolls = 0
            for scroll_number in range(request.max_scrolls + 1):
                for record in await self.parse(page):
                    if matches_search_filters(record, request):
                        records[record.canonical_url] = record
                if request.discovery_method is DiscoveryMethod.SOURCE_URL or len(records) >= request.max_items_per_platform:
                    break
                if scroll_number == request.max_scrolls:
                    break

                height = int(await page.evaluate("document.body.scrollHeight") or 800)
                await page.mouse.wheel(0, max(800, int(height * 0.8)))
                await page.wait_for_timeout(int(request.scroll_pause_seconds * 1000))
                new_height = int(await page.evaluate("document.body.scrollHeight") or 0)
                stagnant_scrolls = stagnant_scrolls + 1 if new_height <= max(previous_height, height) else 0
                previous_height = max(previous_height, new_height)
                if stagnant_scrolls >= 2:
                    break

            for record in list(records.values())[: request.max_items_per_platform]:
                yield record
            if not records:
                raise RuntimeError("PARSER_BROKEN: no video records found")

    async def parse(self, page: Page) -> list[DiscoveredVideo]:
        current_id = tail_id(page.url)
        if current_id:
            record = await self._parse_detail_page(page, current_id)
            return [record] if record else []

        records: dict[str, DiscoveredVideo] = {}
        selector = "a[href*='/reel/'],a[href*='/videos/'],a[href*='/watch'],a[href*='/posts/'],a[href*='story_fbid']"
        for link in await page.locator(selector).all():
            href = await link.get_attribute("href")
            if not href:
                continue
            if href.startswith("/"):
                href = f"https://www.facebook.com{href}"
            video_id = tail_id(href)
            if not video_id:
                continue
            article = link.locator("xpath=ancestor::*[@role='article'][1]")
            has_article = await article.count() > 0
            text = (await article.inner_text()).strip() if has_article else (await link.inner_text()).strip()
            image = article.locator("img[src]").first if has_article else link.locator("img[src]").first
            thumbnail = (await image.get_attribute("src") if await image.count() else None) or ""
            caption, warnings = _extract_caption(text)
            records[canonical_url(href)] = DiscoveredVideo(
                platform=self.platform,
                platform_video_id=video_id,
                canonical_url=canonical_url(href),
                caption=caption,
                hashtags=re.findall(r"#([^\s#]+)", caption),
                thumbnail_url=thumbnail,
                metrics=_extract_metrics(text),
                published_at=await _extract_published_at(article if has_article else page),
                warnings=warnings,
            )
        return list(records.values())

    async def _parse_detail_page(self, page: Page, video_id: str) -> DiscoveredVideo | None:
        description = page.locator("meta[property='og:description'],meta[property='og:title']").first
        image = page.locator("meta[property='og:image']").first
        published = page.locator("meta[property='article:published_time'],time[datetime]").first
        caption = (await description.get_attribute("content") if await description.count() else None) or ""
        thumbnail = (await image.get_attribute("content") if await image.count() else None) or ""
        body_text = await page.locator("body").inner_text()
        published_at = None
        if await published.count():
            value = await published.get_attribute("content") or await published.get_attribute("datetime")
            published_at = _parse_datetime(value)
        caption, warnings = _extract_caption(caption)
        return DiscoveredVideo(
            platform=self.platform,
            platform_video_id=video_id,
            canonical_url=canonical_url(page.url),
            caption=caption,
            hashtags=re.findall(r"#([^\s#]+)", caption),
            thumbnail_url=thumbnail,
            metrics=_extract_metrics(body_text),
            published_at=published_at,
            warnings=warnings,
        )


def matches_search_filters(video: DiscoveredVideo, request: CrawlJobRequest) -> bool:
    """Apply explicit criteria; unknown metrics never match a minimum."""
    criteria = {
        "views": request.min_views,
        "likes": request.min_likes,
        "comments": request.min_comments,
        "shares": request.min_shares,
    }
    for name, minimum in criteria.items():
        if minimum is not None and (name not in video.metrics or float(video.metrics[name]) < minimum):
            return False
    if request.published_after and (video.published_at is None or video.published_at < request.published_after):
        return False
    if request.published_before and (video.published_at is None or video.published_at > request.published_before):
        return False
    return True


def _extract_metrics(text: str) -> dict[str, int | float]:
    patterns = {
        "views": r"(?P<value>[\d.,]+\s*[KMB]?)\s*(?:views?|lượt xem)",
        "likes": r"(?P<value>[\d.,]+\s*[KMB]?)\s*(?:likes?|reactions?|lượt thích)",
        "comments": r"(?P<value>[\d.,]+\s*[KMB]?)\s*(?:comments?|bình luận)",
        "shares": r"(?P<value>[\d.,]+\s*[KMB]?)\s*(?:shares?|lượt chia sẻ)",
    }
    metrics: dict[str, int | float] = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            metrics[name] = _parse_count(match.group("value"))
    return metrics


def _parse_count(value: str) -> int | float:
    normalized = value.strip().upper().replace(" ", "")
    multiplier = 1
    if normalized[-1:] in {"K", "M", "B"}:
        multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}[normalized[-1]]
        normalized = normalized[:-1]
    if multiplier == 1:
        return int(float(normalized.replace(",", "")))
    result = float(normalized.replace(",", ".")) * multiplier
    return int(result) if result.is_integer() else result


def _extract_caption(text: str) -> tuple[str, list[str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    caption_lines: list[str] = []
    warnings: list[str] = []
    for line in lines:
        line = re.sub(
            r"[\d.,]+\s*[KMB]?\s*(?:views?|likes?|reactions?|comments?|shares?|lượt xem|lượt thích|bình luận|lượt chia sẻ)\b",
            " ",
            line,
            flags=re.IGNORECASE,
        ).strip(" ·|,-")
        if not line:
            continue
        if line.casefold() in {"like", "comment", "share", "follow", "see more", "see less"}:
            continue
        caption_lines.append(line)
    caption = " ".join(caption_lines).strip()
    if len(caption_lines) > 12 or any(token in caption.casefold() for token in ("log in", "sign up", "create new account")):
        warnings.append("ui_contaminated")
    return caption, warnings


async def _extract_published_at(locator: object) -> datetime | None:
    time_locator = locator.locator("time[datetime]").first  # type: ignore[attr-defined]
    if await time_locator.count():
        return _parse_datetime(await time_locator.get_attribute("datetime"))
    return None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
