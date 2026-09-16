"""IngestVideoFromFileUseCase implementation."""

from dataclasses import dataclass

from module.video_rag.domain.entities.extraction_result import VideoExtractionResult
from module.video_rag.domain.entities.video_record import RawVideoRecord
from module.video_rag.use_case.extract_video_metadata import ExtractVideoMetadataUseCase
from module.video_rag.use_case.ingest_video_data import (
    IngestionResult,
    IngestVideoDataUseCase,
)


@dataclass
class VideoFileIngestionResponse:
    """Detailed response for single-video extraction and ingestion."""

    total_indexed: int
    caption: str
    summary: str
    hashtag: str
    speaker_count: int
    transcript_preview: str
    thumbnail_path: str
    video_url: str
    extraction: VideoExtractionResult


class IngestVideoFromFileUseCase:
    """End-to-end use case: extract metadata from video file on disk, then ingest to vector store."""

    def __init__(
        self,
        extract_use_case: ExtractVideoMetadataUseCase,
        ingest_use_case: IngestVideoDataUseCase,
    ) -> None:
        self._extract = extract_use_case
        self._ingest = ingest_use_case

    async def execute(
        self,
        video_path: str,
        video_url: str | None = None,
        image_url: str | None = None,
        language: str = "vi",
        enable_diarization: bool = True,
    ) -> VideoFileIngestionResponse:
        """Execute extraction and ingest into ChromaDB vector store."""
        # 1. Extract metadata from raw video
        extraction = await self._extract.execute(
            video_path=video_path,
            language=language,
            enable_diarization=enable_diarization,
        )

        # 2. Determine public/storage URLs
        final_video_url = video_url or video_path
        final_image_url = image_url or extraction.thumbnail_path

        # 3. Create standardized RawVideoRecord
        record: RawVideoRecord = extraction.to_raw_video_record(
            video_url=final_video_url,
            image_url=final_image_url,
        )

        # 4. Ingest record through existing pipeline
        raw_dict = {
            "caption": record.caption,
            "hashtag": record.hashtag,
            "transcript": record.transcript,
            "image_url": record.image_url,
            "summary": record.summary,
            "video_url": record.video_url,
        }
        ingest_result: IngestionResult = await self._ingest.execute([raw_dict])

        # 5. Format transcript preview
        preview = (
            extraction.transcript_with_speakers[:500]
            if extraction.transcript_with_speakers
            else extraction.transcript[:500]
        )

        return VideoFileIngestionResponse(
            total_indexed=ingest_result.total_indexed,
            caption=extraction.caption,
            summary=extraction.summary,
            hashtag=extraction.hashtag,
            speaker_count=extraction.speaker_count,
            transcript_preview=preview,
            thumbnail_path=extraction.thumbnail_path,
            video_url=final_video_url,
            extraction=extraction,
        )
