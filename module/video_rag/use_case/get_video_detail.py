"""GetVideoDetailUseCase implementation."""

from dataclasses import dataclass
from typing import Any

from module.video_rag.port.vector_store_port import IVectorStorePort


@dataclass
class VideoDetailResult:
    """Detailed video information excluding id and embedding."""

    caption: str
    hashtag: str
    image_url: str
    video_url: str
    summary: str
    hook_candidate: str
    transcript: str
    transcript_with_speakers: str
    speaker_count: int
    duration_seconds: float
    document: str
    extra_metadata: dict[str, Any]


class GetVideoDetailUseCase:
    """Use case to retrieve comprehensive video information without id and vector."""

    def __init__(self, vector_store: IVectorStorePort) -> None:
        self._vector_store = vector_store

    async def execute(self, video_id: str) -> VideoDetailResult | None:
        """Fetch video record by ID and format detail excluding ID and vector."""
        record = await self._vector_store.get_by_id(video_id)
        if not record:
            return None

        meta = record.get("metadata", {})
        doc = record.get("document", "")

        caption = meta.get("caption", "")
        hashtag = meta.get("hashtag", "")
        summary = meta.get("summary", "")
        image_url = meta.get("image_url", "")
        video_url = meta.get("video_url", "")
        hook = meta.get("hook_candidate", "")
        transcript = meta.get("transcript", "")
        transcript_with_speakers = meta.get("transcript_with_speakers", "")

        # Fallback for older records where transcript wasn't saved in metadata
        if not transcript and not transcript_with_speakers and doc:
            # Document format: "Title: ...\nSummary: ...\nHashtags: ...\nTranscript: ..."
            if "Transcript:" in doc:
                parts = doc.split("Transcript:", 1)
                transcript = parts[1].strip()
                transcript_with_speakers = transcript

        if not transcript_with_speakers and transcript:
            transcript_with_speakers = transcript

        speakers = int(meta.get("speaker_count", 1))
        duration = float(meta.get("duration_seconds", 0.0))

        # Filter out id and vector from extra_metadata
        extra_meta = {
            k: v
            for k, v in meta.items()
            if k
            not in {
                "id",
                "vector",
                "embedding",
                "caption",
                "hashtag",
                "summary",
                "image_url",
                "video_url",
                "hook_candidate",
                "transcript",
                "transcript_with_speakers",
                "speaker_count",
                "duration_seconds",
            }
        }

        return VideoDetailResult(
            caption=caption,
            hashtag=hashtag,
            image_url=image_url,
            video_url=video_url,
            summary=summary,
            hook_candidate=hook,
            transcript=transcript,
            transcript_with_speakers=transcript_with_speakers,
            speaker_count=speakers,
            duration_seconds=duration,
            document=doc,
            extra_metadata=extra_meta,
        )
