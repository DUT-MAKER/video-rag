"""Platform-specific crawlers."""

from module.crawler.platforms.youtube_shorts import (
    YouTubeShortsExtractor,
    YouTubeShortsPipeline,
    YouTubeShortsTranscriptAdapter,
)

__all__ = [
    "YouTubeShortsExtractor",
    "YouTubeShortsTranscriptAdapter",
    "YouTubeShortsPipeline",
]
