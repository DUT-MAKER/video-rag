"""IMediaExtractorPort protocol."""

from typing import Protocol


class IMediaExtractorPort(Protocol):
    """Protocol for extracting audio and keyframes from raw video files."""

    async def extract_audio(
        self,
        video_path: str,
        output_path: str,
    ) -> str:
        """Extract audio as WAV 16kHz mono. Returns output file path."""
        ...

    async def extract_candidate_frames(
        self,
        video_path: str,
        output_dir: str,
        interval_seconds: float = 2.0,
    ) -> list[str]:
        """Extract candidate keyframes at regular intervals and scene changes.

        Returns list of frame image paths.
        """
        ...

    async def get_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""
        ...
