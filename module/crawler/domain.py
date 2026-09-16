"""Multi-platform Domain Models, DTOs, and Exceptions for the Video Crawler."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class PlatformType(str, Enum):
    """Supported video platform sources."""
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"


class IpBlockedStopSignal(Exception):
    """Raised when an external platform blocks the client IP address.
    
    Acts as a circuit breaker signal to halt the crawling job immediately.
    """
    pass


class LLMUnavailableError(Exception):
    """Raised when the LLM service is offline or unreachable."""
    pass


class ExtractionError(Exception):
    """Raised when metadata extraction or media download fails."""
    pass


@dataclass(frozen=True)
class TranscriptSegment:
    """A timestamped segment of spoken text."""
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class TranscriptResult:
    """Consolidated result of speech transcription."""
    full_text: str
    segments: list[TranscriptSegment]
    is_auto_generated: bool = False


@dataclass
class VideoMetadata:
    """Standardized video metadata across all platforms before media download."""
    video_id: str
    platform: PlatformType
    title: str
    description: str
    caption: str
    hashtags: list[str]
    duration: float
    width: int
    height: int
    view_count: int
    like_count: int
    comment_count: int
    upload_date: str
    is_shorts: bool
    raw_info: Optional[dict[str, Any]] = field(default=None, repr=False)


@dataclass
class DownloadedMedia:
    """Local media file paths retrieved during download."""
    video_path: Optional[str]
    thumbnail_path: Optional[str]
