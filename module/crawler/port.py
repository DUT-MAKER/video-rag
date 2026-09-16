"""Common Ports (Interfaces) for the Multi-Platform Video Crawler."""

from typing import Any, Optional, Protocol

from module.crawler.domain import DownloadedMedia, TranscriptResult, VideoMetadata


class IVideoExtractorPort(Protocol):
    """Port for inspecting video metadata and downloading media files."""

    def fetch_metadata(self, video_id: str) -> Optional[VideoMetadata]:
        """Fetches lightweight metadata without downloading the video."""
        ...

    def download_media(
        self,
        video_id: str,
        output_dir: str,
        cached_info: Optional[dict[str, Any]] = None,
    ) -> DownloadedMedia:
        """Downloads full media (video/audio/thumbnail) to the designated output directory."""
        ...


class ITranscriptPort(Protocol):
    """Port for subtitle retrieval and speech transcription."""

    def extract_transcript(
        self,
        video_id: str,
        local_media_path: Optional[str] = None,
    ) -> TranscriptResult:
        """Extracts transcript with timestamps.
        
        Raises:
            IpBlockedStopSignal: If the platform rate-limits the client IP.
        """
        ...


class IStoragePort(Protocol):
    """Port for persisting binary media objects (MinIO or Local Storage)."""

    def upload_file(self, local_path: str, destination_name: str) -> str:
        """Uploads a local file to persistent storage and returns its access URL."""
        ...


class ISummaryPort(Protocol):
    """Port for summarizing video transcript and content using LLM."""

    def summarize(self, caption: str, transcript: str) -> str:
        """Summarizes content into core hooks and key takeaways.
        
        Raises:
            LLMUnavailableError: If the LLM backend cannot produce a summary.
        """
        ...


class IDedupStorePort(Protocol):
    """Port for tracking processed video IDs across runs."""

    def is_processed(self, video_id: str) -> bool:
        """Checks whether the video ID has already been crawled/processed."""
        ...

    def mark_processed(self, video_id: str) -> None:
        """Records the video ID as processed."""
        ...


class IPlatformCrawlerPort(Protocol):
    """Standardized crawler pipeline protocol implemented by each platform."""

    def process_video(self, video_id: str) -> Optional[dict[str, Any]]:
        """Executes full extraction, transcription, and upload for a single video."""
        ...
