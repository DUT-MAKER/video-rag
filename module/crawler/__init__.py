"""Multi-Platform Video Crawler Engine."""

from module.crawler.domain import (
    DownloadedMedia,
    ExtractionError,
    IpBlockedStopSignal,
    LLMUnavailableError,
    PlatformType,
    TranscriptResult,
    TranscriptSegment,
    VideoMetadata,
)
from module.crawler.platforms.youtube_shorts import (
    YouTubeShortsExtractor,
    YouTubeShortsPipeline,
    YouTubeShortsTranscriptAdapter,
)
from module.crawler.port import (
    IDedupStorePort,
    IPlatformCrawlerPort,
    IStoragePort,
    ISummaryPort,
    ITranscriptPort,
    IVideoExtractorPort,
)
from module.crawler.shared import (
    JsonFileDedupStore,
    LLMSummaryAdapter,
    LocalStorageAdapter,
    MinioStorageAdapter,
    WhisperASREngine,
)

__all__ = [
    # Domain
    "PlatformType",
    "VideoMetadata",
    "DownloadedMedia",
    "TranscriptSegment",
    "TranscriptResult",
    "IpBlockedStopSignal",
    "LLMUnavailableError",
    "ExtractionError",
    # Ports
    "IVideoExtractorPort",
    "ITranscriptPort",
    "IStoragePort",
    "ISummaryPort",
    "IDedupStorePort",
    "IPlatformCrawlerPort",
    # Shared Infra
    "MinioStorageAdapter",
    "LocalStorageAdapter",
    "LLMSummaryAdapter",
    "JsonFileDedupStore",
    "WhisperASREngine",
    # Platforms
    "YouTubeShortsExtractor",
    "YouTubeShortsTranscriptAdapter",
    "YouTubeShortsPipeline",
]
