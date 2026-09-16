"""Facebook public video/reel discovery adapter."""

import re

from playwright.async_api import Page

from video_crawler.crawlers.base import BrowserPlatformCrawler, encoded
from video_crawler.domain import CrawlJobRequest, DiscoveredVideo, DiscoveryMethod, Platform
from video_crawler.infrastructure.browser import canonical_url, tail_id


class FacebookCrawler(BrowserPlatformCrawler):
    platform = Platform.FACEBOOK

    def build_url(self, request: CrawlJobRequest) -> str:
        value = request.value_for(self.platform)
        if request.discovery_method is DiscoveryMethod.SOURCE_URL:
            return value
        if request.discovery_method is DiscoveryMethod.CREATOR:
            return f"https://www.facebook.com/{encoded(value)}/reels"
        return f"https://www.facebook.com/search/videos?q={encoded(value.lstrip('#'))}"

    async def parse(self, page: Page) -> list[DiscoveredVideo]:
        current_id = tail_id(page.url)
        if current_id:
            description = page.locator("meta[property='og:description'],meta[property='og:title']").first
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
        selector = "a[href*='/reel/'],a[href*='/videos/'],a[href*='story_fbid']"
        for link in await page.locator(selector).all():
            href = await link.get_attribute("href")
            if not href:
                continue
            if href.startswith("/"):
                href = f"https://www.facebook.com{href}"
            video_id = tail_id(href)
            if not video_id:
                continue
            article = link.locator("xpath=ancestor::div[@role='article'][1]")
            caption = (
                (await article.inner_text()).strip()
                if await article.count()
                else (await link.inner_text()).strip()
            )
            image = article.locator("img[src]").first if await article.count() else link.locator("img[src]").first
            tags = re.findall(r"#([^\s#]+)", caption)
            records[video_id] = DiscoveredVideo(
                platform=self.platform,
                platform_video_id=video_id,
                canonical_url=canonical_url(href),
                caption=caption,
                hashtags=tags,
                thumbnail_url=(await image.get_attribute("src") if await image.count() else None) or "",
            )
        return list(records.values())
