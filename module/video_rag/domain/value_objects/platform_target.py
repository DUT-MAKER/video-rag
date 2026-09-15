"""PlatformTarget enumeration."""

from enum import Enum


class PlatformTarget(str, Enum):
    """Supported short-form social video platforms."""

    TIKTOK = "tiktok"
    REELS = "reels"
    SHORTS = "shorts"
    ALL = "all"
