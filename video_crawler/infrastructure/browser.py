"""Conservative Playwright context and shared parsing helpers."""

from __future__ import annotations

import re
from contextlib import asynccontextmanager
from typing import AsyncIterator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from playwright.async_api import BrowserContext, Page, async_playwright

from video_crawler.config import CrawlerSettings
from video_crawler.domain import Platform


class BrowserContextFactory:
    def __init__(self, settings: CrawlerSettings) -> None:
        self.settings = settings

    @asynccontextmanager
    async def open(self, platform: Platform) -> AsyncIterator[BrowserContext]:
        session = self.settings.session_file(platform.value)
        if platform in {Platform.FACEBOOK, Platform.TIKTOK} and not session.exists():
            raise RuntimeError(f"AUTH_REQUIRED: missing {platform.value} session")
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.settings.browser_headless)
            options: dict[str, object] = {"locale": "en-US"}
            if session.exists():
                options["storage_state"] = str(session)
            context = await browser.new_context(**options)
            try:
                yield context
            finally:
                await context.close()
                await browser.close()


async def assert_page_access(page: Page) -> None:
    body = (await page.locator("body").inner_text()).casefold()
    if any(item in body for item in ("captcha", "verify you are human", "security check")):
        raise RuntimeError("CHALLENGE_REQUIRED: platform challenge detected")
    if any(item in body for item in ("log in to continue", "login to continue", "sign in to continue")):
        raise RuntimeError("AUTH_REQUIRED: platform login wall detected")


def canonical_url(value: str) -> str:
    parsed = urlparse(value)
    retained = {
        key: values
        for key, values in parse_qs(parsed.query).items()
        if key in {"v", "story_fbid", "id"}
    }
    return urlunparse(
        (
            parsed.scheme or "https",
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",
            urlencode(retained, doseq=True),
            "",
        )
    )


def tail_id(value: str) -> str:
    parsed = urlparse(value)
    if parsed.hostname and parsed.hostname.lower().endswith("youtu.be"):
        return parsed.path.strip("/").split("/", 1)[0]
    match = re.search(r"/(?:video|videos|reel|posts)/([A-Za-z0-9_-]+)", value)
    if match:
        return match.group(1)
    query = parse_qs(parsed.query)
    for key in ("v", "story_fbid"):
        if query.get(key):
            return query[key][0]
    return ""
