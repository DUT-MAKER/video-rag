"""RawVideoRecord entity."""

import hashlib
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class RawVideoRecord:
    """Represents an ingested viral video record from the knowledge store."""

    caption: str
    hashtag: str
    transcript: str
    image_url: str
    summary: str
    video_url: str
    id: str = ""
    speaker_count: int = 1
    duration_seconds: float = 0.0
    transcript_with_speakers: str = ""
    segments: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        if not self.id:
            # Generate deterministic identifier from video URL, caption, or transcript
            source_seed = self.video_url or self.caption or self.transcript
            self.id = hashlib.sha256(source_seed.encode("utf-8")).hexdigest()[:16]

    def extract_hook(self, max_words: int = 35) -> str:
        """Extract the opening 3-5 second hook candidate from the transcript."""
        clean_text = self.transcript.strip()
        if not clean_text:
            return self.caption.strip()

        # Split by first sentence delimiter
        sentences = re.split(r"(?<=[.!?…])\s+", clean_text)
        if sentences and len(sentences[0].split()) >= 4:
            first_sentence = sentences[0].strip()
            words = first_sentence.split()
            if len(words) <= max_words:
                return first_sentence
            return " ".join(words[:max_words]) + "..."

        # Fallback to taking max_words from the start
        words = clean_text.split()
        if len(words) <= max_words:
            return clean_text
        return " ".join(words[:max_words]) + "..."

    def to_searchable_text(self) -> str:
        """Compose rich semantic text representation for vector embedding."""
        parts = []
        if self.caption:
            parts.append(f"Title: {self.caption}")
        if self.summary:
            parts.append(f"Summary: {self.summary}")
        if self.hashtag:
            parts.append(f"Hashtags: {self.hashtag}")
        if self.transcript:
            parts.append(f"Transcript: {self.transcript}")
        return "\n".join(parts)

    def to_metadata(self) -> dict[str, Any]:
        """Convert record attributes into vector store metadata."""
        return {
            "caption": self.caption,
            "hashtag": self.hashtag,
            "image_url": self.image_url,
            "summary": self.summary,
            "video_url": self.video_url,
            "hook_candidate": self.extract_hook(),
            "transcript": self.transcript,
            "transcript_with_speakers": self.transcript_with_speakers or self.transcript,
            "speaker_count": self.speaker_count,
            "duration_seconds": self.duration_seconds,
            "segments": self.segments or [],
        }
