"""TikTok discovery adapter."""

import json
import re
from datetime import UTC, datetime

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

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
        video_links = page.locator("a[href*='/video/']")
        try:
            await video_links.first.wait_for(state="attached", timeout=15_000)
        except PlaywrightTimeoutError:
            payloads = await page.locator("script[type='application/json']").all_text_contents()
            return self._parse_hydration_payloads(payloads)
        records: dict[str, DiscoveredVideo] = {}
        snapshots = await video_links.evaluate_all(
            """
            links => links.map(link => {
                const image = link.querySelector('img[alt]');
                return {
                    href: link.href || '',
                    caption: (image?.alt || link.innerText || '').trim(),
                    thumbnail: image?.src || '',
                };
            })
            """
        )
        for snapshot in snapshots:
            href = str(snapshot.get("href") or "")
            if not href:
                continue
            if href.startswith("/"):
                href = f"https://www.tiktok.com{href}"
            video_id = tail_id(href)
            if not video_id:
                continue
            caption = str(snapshot.get("caption") or "")
            tags = re.findall(r"#([^\s#]+)", caption)
            records[video_id] = DiscoveredVideo(
                platform=self.platform,
                platform_video_id=video_id,
                canonical_url=canonical_url(href),
                caption=caption.strip(),
                hashtags=tags,
                thumbnail_url=str(snapshot.get("thumbnail") or ""),
            )
        return list(records.values())

    @classmethod
    def _parse_hydration_payloads(cls, payloads: list[str]) -> list[DiscoveredVideo]:
        records: dict[str, DiscoveredVideo] = {}

        def walk(value: object) -> None:
            if isinstance(value, list):
                for child in value:
                    walk(child)
                return
            if not isinstance(value, dict):
                return

            video_id = str(value.get("id") or "")
            author = value.get("author")
            if video_id.isdigit() and len(video_id) >= 15 and isinstance(author, dict):
                username = str(author.get("uniqueId") or "").strip()
                caption_value = value.get("desc")
                if username and caption_value is not None:
                    caption = str(caption_value).strip()
                    stats = value.get("stats") if isinstance(value.get("stats"), dict) else {}
                    video = value.get("video") if isinstance(value.get("video"), dict) else {}
                    timestamp = value.get("createTime")
                    published_at = None
                    if str(timestamp or "").isdigit():
                        published_at = datetime.fromtimestamp(int(str(timestamp)), tz=UTC)
                    records[video_id] = DiscoveredVideo(
                        platform=cls.platform,
                        platform_video_id=video_id,
                        canonical_url=f"https://www.tiktok.com/@{username}/video/{video_id}",
                        caption=caption,
                        hashtags=re.findall(r"#([^\s#]+)", caption),
                        thumbnail_url=str(
                            video.get("cover")
                            or video.get("originCover")
                            or video.get("dynamicCover")
                            or ""
                        ),
                        metrics=cls._stats(stats),
                        published_at=published_at,
                    )
            for child in value.values():
                walk(child)

        for payload in payloads:
            try:
                walk(json.loads(payload))
            except json.JSONDecodeError:
                continue
        return list(records.values())

    @staticmethod
    def _stats(stats: dict[object, object]) -> dict[str, int | float]:
        result: dict[str, int | float] = {}
        fields = {
            "playCount": "view_count",
            "diggCount": "like_count",
            "commentCount": "comment_count",
            "shareCount": "share_count",
        }
        for source, target in fields.items():
            value = stats.get(source)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                result[target] = value
        return result
