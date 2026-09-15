"""PlatformTarget value object."""

from enum import StrEnum


class PlatformTarget(StrEnum):
    """Target short-form video publishing platform."""

    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
