"""ITranscriberPort protocol and TranscriptionResult dataclass."""

from dataclasses import dataclass, field
from typing import Protocol

from module.video_rag.domain.entities.extraction_result import TranscriptSegment


@dataclass
class TranscriptionResult:
    """Result of speech-to-text transcription with speaker diarization."""

    full_text: str  # Plain text without speakers
    segments: list[TranscriptSegment] = field(default_factory=list)  # Speaker-attributed segments
    speaker_count: int = 0  # Number of distinct speakers detected
    language: str = "vi"
    duration_seconds: float = 0.0


class ITranscriberPort(Protocol):
    """Protocol for speech-to-text transcription with speaker diarization."""

    async def transcribe(
        self,
        audio_path: str,
        language: str = "vi",
        enable_diarization: bool = True,
    ) -> TranscriptionResult:
        """Transcribe audio to text with timestamps and speaker attribution.

        Args:
            audio_path: Path to WAV audio file (16kHz mono).
            language: Language code (default: "vi" for Vietnamese).
            enable_diarization: If True, perform speaker diarization.

        Returns:
            TranscriptionResult with full_text, speaker-attributed segments,
            and speaker count.
        """
        ...
