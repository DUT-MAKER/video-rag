"""Deterministic, editable daily crawler schedule."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from video_crawler.domain import Platform


VIETNAM_TIME = timezone(timedelta(hours=7))
PLATFORM_OFFSET = {Platform.FACEBOOK: 0, Platform.TIKTOK: 1, Platform.YOUTUBE: 2}


@dataclass(frozen=True)
class ScheduleConfig:
    keywords: tuple[str, ...]
    hours: tuple[int, ...] = (0, 2, 4, 22)
    links_per_platform: int = 10
    timezone: str = "Asia/Ho_Chi_Minh"
    grace_minutes: int = 30
    max_attempts: int = 3
    retry_delay_seconds: int = 60

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "ScheduleConfig":
        keywords = tuple(str(item).strip() for item in value.get("keywords", []))
        hours = tuple(sorted(int(hour) for hour in value.get("hours", [0, 2, 4, 22])))
        config = cls(
            keywords=keywords,
            hours=hours,
            links_per_platform=int(value.get("links_per_platform", 10)),
            timezone=str(value.get("timezone", "Asia/Ho_Chi_Minh")),
            grace_minutes=int(value.get("grace_minutes", 30)),
            max_attempts=int(value.get("max_attempts", 3)),
            retry_delay_seconds=int(value.get("retry_delay_seconds", 60)),
        )
        if not keywords or any(not word for word in keywords) or len(set(keywords)) != len(keywords):
            raise ValueError("keywords must be non-empty and unique")
        if not hours or len(set(hours)) != len(hours) or any(not 0 <= hour <= 23 for hour in hours):
            raise ValueError("hours must be unique values from 0 to 23")
        if config.timezone != "Asia/Ho_Chi_Minh":
            raise ValueError("only Asia/Ho_Chi_Minh timezone is supported")
        if not 1 <= config.links_per_platform <= 100:
            raise ValueError("links_per_platform must be between 1 and 100")
        if not 1 <= config.grace_minutes <= 59 or not 1 <= config.max_attempts <= 10:
            raise ValueError("invalid grace_minutes or max_attempts")
        if config.retry_delay_seconds < 1:
            raise ValueError("retry_delay_seconds must be positive")
        return config

    @classmethod
    def from_file(cls, path: Path) -> "ScheduleConfig":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


@dataclass(frozen=True)
class ScheduledSlot:
    key: str
    keyword: str
    platform: Platform
    limit: int


def due_slot(config: ScheduleConfig, platform: Platform, now: datetime) -> ScheduledSlot | None:
    local = now.astimezone(VIETNAM_TIME)
    if local.hour not in config.hours or local.minute >= config.grace_minutes:
        return None
    position = config.hours.index(local.hour)
    rotation = (local.date().toordinal() * len(config.hours) + position + PLATFORM_OFFSET[platform])
    keyword = config.keywords[rotation % len(config.keywords)]
    key = f"{local.date().isoformat()}:{local.hour:02d}:00:{platform.value}"
    return ScheduledSlot(key=key, keyword=keyword, platform=platform, limit=config.links_per_platform)
