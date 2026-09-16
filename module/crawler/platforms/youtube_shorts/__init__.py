"""YouTube Shorts crawler platform package."""

from module.crawler.platforms.youtube_shorts.extractor import YouTubeShortsExtractor
from module.crawler.platforms.youtube_shorts.pipeline import YouTubeShortsPipeline
from module.crawler.platforms.youtube_shorts.transcript import (
    YouTubeShortsTranscriptAdapter,
)

__all__ = [
    "YouTubeShortsExtractor",
    "YouTubeShortsTranscriptAdapter",
    "YouTubeShortsPipeline",
]
