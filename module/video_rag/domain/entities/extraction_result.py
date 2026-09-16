"""Domain entities for video extraction pipeline."""

from dataclasses import dataclass, field
from module.video_rag.domain.entities.video_record import RawVideoRecord


@dataclass
class TranscriptSegment:
    """A single timestamped, speaker-attributed segment from STT + diarization."""

    start: float  # seconds
    end: float  # seconds
    text: str
    speaker: str  # e.g. "SPEAKER_00", "SPEAKER_01"


@dataclass
class VideoExtractionResult:
    """Complete result of extracting metadata from a raw video file."""

    video_path: str
    transcript: str  # Full transcript (plain text)
    transcript_with_speakers: str  # Transcript with speaker labels
    transcript_segments: list[TranscriptSegment] = field(default_factory=list)
    speaker_count: int = 0  # Number of distinct speakers
    caption: str = ""  # AI-generated viral caption
    hashtag: str = ""  # AI-generated hashtags
    summary: str = ""  # AI-generated summary
    thumbnail_path: str = ""  # Path to selected best thumbnail
    duration_seconds: float = 0.0

    def format_speaker_transcript(self) -> str:
        """Format transcript with speaker labels for display and RAG context."""
        lines = []
        for seg in self.transcript_segments:
            timestamp = f"[{seg.start:.1f}s -> {seg.end:.1f}s]"
            lines.append(f"{seg.speaker} {timestamp}: {seg.text}")
        return "\n".join(lines)

    def to_raw_video_record(self, video_url: str, image_url: str) -> RawVideoRecord:
        """Convert extraction result into standard RawVideoRecord for ingestion."""
        return RawVideoRecord(
            caption=self.caption,
            hashtag=self.hashtag,
            transcript=self.transcript_with_speakers or self.transcript,
            image_url=image_url,
            summary=self.summary,
            video_url=video_url,
        )
