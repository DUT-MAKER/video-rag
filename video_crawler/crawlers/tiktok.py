"""TikTok discovery adapter."""

import re

from playwright.async_api import Page

from video_crawler.crawlers.base import BrowserPlatformCrawler, encoded
from video_crawler.domain import CrawlJobRequest, DiscoveredVideo, DiscoveryMethod, Platform
from video_crawler.infrastructure.browser import canonical_url, tail_id


class TikTokCrawler(BrowserPlatformCrawler):
    platform = Platform.TIKTOK

    def build_url(self, request: CrawlJobRequest) -> str:
        value = request.value_for(self.platform)
        if request.discovery_method is DiscoveryMethod.SOURCE_URL:
            return value
        if request.discovery_method is DiscoveryMethod.CREATOR:
            return f"https://www.tiktok.com/@{encoded(value.lstrip('@'))}"
        if request.discovery_method is DiscoveryMethod.HASHTAG:
            return f"https://www.tiktok.com/tag/{encoded(value.lstrip('#'))}"
        return f"https://www.tiktok.com/search?q={encoded(value)}"

    async def parse(self, page: Page) -> list[DiscoveredVideo]:
        current_id = tail_id(page.url)
        if current_id:
            description = page.locator("meta[property='og:description']").first
            image = page.locator("meta[property='og:image']").first
            caption = (await description.get_attribute("content") if await description.count() else None) or ""
            return [
                DiscoveredVideo(
                    platform=self.platform,
                    platform_video_id=current_id,
                    canonical_url=canonical_url(page.url),
                    caption=caption.strip(),
                    hashtags=re.findall(r"#([^\s#]+)", caption),
                    thumbnail_url=(await image.get_attribute("content") if await image.count() else None) or "",
                )
            ]
        records: dict[str, DiscoveredVideo] = {}
        for link in await page.locator("a[href*='/video/']").all():
            href = await link.get_attribute("href")
            if not href:
                continue
            if href.startswith("/"):
                href = f"https://www.tiktok.com{href}"
            video_id = tail_id(href)
            if not video_id:
                continue
            image = link.locator("img[alt]").first
            caption = (await image.get_attribute("alt") if await image.count() else None) or (await link.inner_text())
            tags = re.findall(r"#([^\s#]+)", caption)
            records[video_id] = DiscoveredVideo(
                platform=self.platform,
                platform_video_id=video_id,
                canonical_url=canonical_url(href),
                caption=caption.strip(),
                hashtags=tags,
                thumbnail_url=(await image.get_attribute("src") if await image.count() else None) or "",
            )
        return list(records.values())
