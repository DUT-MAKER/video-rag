"""Operator-driven Playwright login; session values never cross an API boundary."""

from __future__ import annotations

import asyncio
import json
import os
import secrets
from pathlib import Path

from playwright.async_api import BrowserContext, async_playwright

from video_crawler.config import CrawlerSettings
from video_crawler.domain import Platform

LOGIN_URLS = {
    Platform.FACEBOOK: "https://www.facebook.com/login",
    Platform.TIKTOK: "https://www.tiktok.com/login",
    Platform.YOUTUBE: "https://accounts.google.com/ServiceLogin?service=youtube",
}
AUTH_COOKIES = {
    Platform.FACEBOOK: {"c_user"},
    Platform.TIKTOK: {"sessionid", "sessionid_ss"},
    Platform.YOUTUBE: {"SAPISID", "__Secure-3PAPISID"},
}


class SessionManager:
    def __init__(self, settings: CrawlerSettings) -> None:
        self.settings = settings

    def status(self, platform: Platform) -> dict[str, str | bool | None]:
        path = self.settings.session_file(platform.value)
        return {
            "platform": platform.value,
            "configured": path.exists(),
            "state": "stored" if path.exists() else "not_configured",
            "path_hint": path.name if path.exists() else None,
        }

    async def login(self, platform: Platform) -> Path:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(LOGIN_URLS[platform], wait_until="domcontentloaded")
            await asyncio.to_thread(input, "Complete login in the browser, then press Enter here: ")
            await self._save(platform, context)
            await context.close()
            await browser.close()
        return self.settings.session_file(platform.value)

    async def _save(self, platform: Platform, context: BrowserContext) -> None:
        payload = await context.storage_state()
        names = {str(cookie.get("name")) for cookie in payload.get("cookies", [])}
        if not names.intersection(AUTH_COOKIES[platform]):
            raise RuntimeError(f"Login was not detected for {platform.value}")
        path = self.settings.session_file(platform.value)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")
        temporary.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
        temporary.chmod(0o600)
        os.replace(temporary, path)
