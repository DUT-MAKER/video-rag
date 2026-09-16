"""Unified IngestVideoDataUseCase implementation."""

from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger

from module.video_rag.domain.entities.extraction_result import VideoExtractionResult
from module.video_rag.domain.entities.video_record import RawVideoRecord
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.vector_store_port import IVectorStorePort
from module.video_rag.service.video_extraction_service import (
    VideoExtractionPipelineService,
)


@dataclass
class VideoItemInput:
    """Input specification for a single video item."""

    video_path: str
    caption: str = ""
    hashtag: str = ""
    language: str = "vi"
    video_url: str = ""


@dataclass
class IngestionResult:
    """Comprehensive summary of data ingestion operation."""

    total_processed: int
    total_indexed: int
    extracted_hooks: list[str] = field(default_factory=list)
    indexed_ids: list[str] = field(default_factory=list)
    records: list[RawVideoRecord] = field(default_factory=list)
    extractions: list[VideoExtractionResult] = field(default_factory=list)

    @property
    def latest_extraction(self) -> VideoExtractionResult | None:
        return self.extractions[0] if self.extractions else None

    @property
    def latest_record(self) -> RawVideoRecord | None:
        return self.records[0] if self.records else None


class IngestVideoDataUseCase:
    """Single unified use case to extract video metadata, merge input metadata, and ingest into Vector Store."""

    def __init__(
        self,
        embedding_port: IEmbeddingPort,
        vector_store_port: IVectorStorePort,
        extract_service: VideoExtractionPipelineService,
    ) -> None:
        self._embed = embedding_port
        self._vector_store = vector_store_port
        self._extract = extract_service

    async def execute(
        self,
        input_data: VideoItemInput,
    ) -> IngestionResult:
        """Execute extraction and ingestion for a single video item.

        Args:
            input_data: VideoItemInput instance or raw dictionary.

        Returns:
            IngestionResult containing indexed IDs, extracted hooks, records, and extractions.
        """
        video_path = input_data.video_path
        extractions: list[VideoExtractionResult] = []

        logger.info(f"▶️ [IngestVideoDataUseCase] Bắt đầu xử lý video item: '{video_path}'")

        # 1. Run extraction for raw video file
        logger.info("⚙️ [IngestVideoDataUseCase] Giai đoạn 1: Gọi VideoExtractionPipelineService...")
        extraction = await self._extract.execute(
            video_path=str(video_path),
            language=input_data.language,
        )
        extractions.append(extraction)
        logger.info(
            f"✅ [IngestVideoDataUseCase] Giai đoạn 1 hoàn tất "
            f"(Speakers: {extraction.speaker_count}, Duration: {extraction.duration_seconds:.1f}s)"
        )

        final_caption = input_data.caption or extraction.caption
        final_hashtag = input_data.hashtag or extraction.hashtag
        final_summary = extraction.summary
        final_video_url = input_data.video_url or str(video_path)
        final_image_url = extraction.thumbnail_path
        segments_dict = [
            {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
                "speaker": seg.speaker,
            }
            for seg in extraction.transcript_segments
        ]

        record = RawVideoRecord(
            caption=final_caption,
            hashtag=final_hashtag,
            transcript=extraction.transcript,
            image_url=final_image_url,
            summary=final_summary,
            video_url=final_video_url,
            speaker_count=extraction.speaker_count,
            duration_seconds=extraction.duration_seconds,
            transcript_with_speakers=extraction.transcript_with_speakers,
            segments=segments_dict,
        )

        # 2. Embed and upsert into Vector Store
        texts_to_embed = [record.to_searchable_text()]
        ids: list[str] = [record.id]
        metadatas = [record.to_metadata()]
        extracted_hooks = [record.extract_hook()]

        logger.info(f"🔢 [IngestVideoDataUseCase] Giai đoạn 2: Tạo vector embedding cho record '{record.id}'...")
        vectors = await self._embed.get_embeddings(texts_to_embed)
        logger.info(f"✅ [IngestVideoDataUseCase] Đã tạo embedding (dim: {len(vectors[0]) if vectors else 0})")

        logger.info("💾 [IngestVideoDataUseCase] Giai đoạn 3: Lưu vào Vector Store (PostgreSQL pgvector)...")
        await self._vector_store.upsert_batch(
            ids=ids,
            vectors=vectors,
            metadatas=metadatas,
            documents=texts_to_embed,
        )
        logger.info(f"✅ [IngestVideoDataUseCase] Upsert thành công record id: {ids}")

        return IngestionResult(
            total_processed=1,
            total_indexed=1,
            extracted_hooks=extracted_hooks,
            indexed_ids=ids,
            records=[record],
            extractions=extractions,
        )
