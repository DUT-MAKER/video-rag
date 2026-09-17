"""Operator-driven Playwright login; session values never cross an API boundary."""

from __future__ import annotations

import asyncio
import json
import os
import secrets
from contextlib import suppress
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
COOKIE_DOMAINS = {
    Platform.FACEBOOK: ".facebook.com",
    Platform.TIKTOK: ".tiktok.com",
    Platform.YOUTUBE: ".youtube.com",
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
        profile_dir = self.settings.browser_profile_dir(platform.value)
        profile_dir.mkdir(parents=True, exist_ok=True)
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                channel="chrome",
                headless=False,
                no_viewport=True,
                args=["--start-maximized"],
            )
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                await page.goto(LOGIN_URLS[platform], wait_until="domcontentloaded")
                await asyncio.to_thread(
                    input,
                    "Complete login in Chrome, then press Enter here: ",
                )
                await self._save(platform, context)
            finally:
                with suppress(Exception):
                    await context.close()
        return self.settings.session_file(platform.value)

    def import_cookie_header(self, platform: Platform, source: Path) -> Path:
        raw_header = source.read_text(encoding="utf-8").strip()
        if raw_header.casefold().startswith("cookie:"):
            raw_header = raw_header.split(":", 1)[1].strip()
        cookies: list[dict[str, object]] = []
        for item in raw_header.split(";"):
            name, separator, value = item.strip().partition("=")
            if not separator or not name or not value:
                continue
            cookies.append(
                {
                    "name": name,
                    "value": value,
                    "domain": COOKIE_DOMAINS[platform],
                    "path": "/",
                    "expires": -1,
                    "httpOnly": name in AUTH_COOKIES[platform],
                    "secure": True,
                    "sameSite": "Lax",
                }
            )
        self._validate_auth_cookies(platform, cookies)
        return self._write_state(platform, {"cookies": cookies, "origins": []})

    async def _save(self, platform: Platform, context: BrowserContext) -> None:
        payload = await context.storage_state()
        self._validate_auth_cookies(platform, payload.get("cookies", []))
        self._write_state(platform, payload)

    @staticmethod
    def _validate_auth_cookies(
        platform: Platform,
        cookies: list[dict[str, object]],
    ) -> None:
        names = {str(cookie.get("name")) for cookie in cookies}
        if not names.intersection(AUTH_COOKIES[platform]):
            raise RuntimeError(f"Login was not detected for {platform.value}")

    def _write_state(self, platform: Platform, payload: dict[str, object]) -> Path:
        path = self.settings.session_file(platform.value)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{secrets.token_hex(6)}.tmp")
        temporary.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
        temporary.chmod(0o600)
        os.replace(temporary, path)
        return path
