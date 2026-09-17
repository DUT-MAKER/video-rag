"""YouTube discovery adapter."""

from urllib.parse import quote_plus

from playwright.async_api import Page

from video_crawler.crawlers.base import BrowserPlatformCrawler
from video_crawler.domain import CrawlJobRequest, DiscoveredVideo, DiscoveryMethod, Platform
from video_crawler.infrastructure.browser import canonical_url, tail_id


class YouTubeCrawler(BrowserPlatformCrawler):
    platform = Platform.YOUTUBE

    def build_url(self, request: CrawlJobRequest) -> str:
        value = request.value_for(self.platform)
        if request.discovery_method is DiscoveryMethod.SOURCE_URL:
            return value
        if request.discovery_method is DiscoveryMethod.CREATOR:
            return f"https://www.youtube.com/@{quote_plus(value.lstrip('@'))}/shorts"
        return f"https://www.youtube.com/results?search_query={quote_plus(value)}"

    async def parse(self, page: Page) -> list[DiscoveredVideo]:
        current_id = tail_id(page.url)
        if current_id:
            title = page.locator("meta[name='title'],meta[property='og:title']").first
            image = page.locator("meta[property='og:image']").first
            caption = (await title.get_attribute("content") if await title.count() else None) or ""
            return [
                DiscoveredVideo(
                    platform=self.platform,
                    platform_video_id=current_id,
                    canonical_url=canonical_url(page.url),
                    caption=caption.strip(),
                    thumbnail_url=(await image.get_attribute("content") if await image.count() else None) or "",
                )
            ]
        records: dict[str, DiscoveredVideo] = {}
        selector = "a[href*='/shorts/'], a#video-title[href*='/watch']"
        for link in await page.locator(selector).all():
            href = await link.get_attribute("href")
            if not href:
                continue
            if href.startswith("/"):
                href = f"https://www.youtube.com{href}"
            video_id = tail_id(href)
            if not video_id:
                continue
            caption = (
                await link.get_attribute("title")
                or await link.get_attribute("aria-label")
                or await link.inner_text()
            ).strip()
            container = link.locator(
                "xpath=ancestor::*[self::ytd-video-renderer or self::ytd-rich-item-renderer][1]"
            )
            thumbnail_node = container.locator("img").first
            thumbnail = (
                await thumbnail_node.get_attribute("src")
                if await thumbnail_node.count()
                else None
            )
            records[video_id] = DiscoveredVideo(
                platform=self.platform,
                platform_video_id=video_id,
                canonical_url=canonical_url(href),
                caption=caption,
                thumbnail_url=thumbnail or "",
            )
        return list(records.values())
