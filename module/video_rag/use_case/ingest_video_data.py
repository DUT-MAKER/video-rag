"""Unified IngestVideoDataUseCase implementation."""

from __future__ import annotations

from dataclasses import dataclass, field

import hashlib
import mimetypes
import os
from pathlib import Path

from loguru import logger

from core.config import s3_settings
from module.upload.port.s3_client import IS3Client
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
        s3_client: IS3Client | None = None,
    ) -> None:
        self._embed = embedding_port
        self._vector_store = vector_store_port
        self._extract = extract_service
        self._s3 = s3_client

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

        # Merge extracted information with user-provided metadata
        final_caption = input_data.caption or extraction.caption
        final_hashtag = input_data.hashtag or extraction.hashtag
        final_summary = extraction.summary
        final_video_url = input_data.video_url or str(video_path)
        final_image_url = extraction.thumbnail_path

        # Generate deterministic record ID
        seed = f"{video_path}_{final_caption}_{extraction.transcript[:100]}"
        record_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]

        # 2. Upload video & thumbnail to S3/MinIO if s3_client is available
        if self._s3 is not None and s3_settings.bucket_name:
            bucket = s3_settings.bucket_name

            # 2.1 Upload video file if local path exists
            if os.path.exists(str(video_path)):
                try:
                    ext = Path(str(video_path)).suffix or ".mp4"
                    video_key = f"videos/{record_id}{ext}"
                    content_type, _ = mimetypes.guess_type(str(video_path))
                    content_type = content_type or "video/mp4"

                    logger.info(
                        f"☁️ [IngestVideoDataUseCase] Đang upload video lên S3/MinIO: s3://{bucket}/{video_key}..."
                    )
                    self._s3.upload_file(
                        file_path=str(video_path),
                        bucket=bucket,
                        key=video_key,
                        content_type=content_type,
                    )
                    final_video_url = self._s3.get_object_url(bucket=bucket, key=video_key)
                    logger.info(
                        f"✅ [IngestVideoDataUseCase] Upload video thành công! MinIO URL: {final_video_url}"
                    )
                except Exception as exc:
                    logger.warning(
                        f"⚠️ [IngestVideoDataUseCase] Không thể upload video lên S3/MinIO ({exc}), dùng URL cục bộ: {final_video_url}"
                    )

            # 2.2 Upload thumbnail file if local path exists
            if extraction.thumbnail_path and os.path.exists(extraction.thumbnail_path):
                try:
                    ext = Path(extraction.thumbnail_path).suffix or ".jpg"
                    thumb_key = f"thumbnails/{record_id}{ext}"
                    content_type, _ = mimetypes.guess_type(extraction.thumbnail_path)
                    content_type = content_type or "image/jpeg"

                    logger.info(
                        f"☁️ [IngestVideoDataUseCase] Đang upload thumbnail lên S3/MinIO: s3://{bucket}/{thumb_key}..."
                    )
                    self._s3.upload_file(
                        file_path=extraction.thumbnail_path,
                        bucket=bucket,
                        key=thumb_key,
                        content_type=content_type,
                    )
                    final_image_url = self._s3.get_object_url(bucket=bucket, key=thumb_key)
                    logger.info(
                        f"✅ [IngestVideoDataUseCase] Upload thumbnail thành công! MinIO URL: {final_image_url}"
                    )
                except Exception as exc:
                    logger.warning(
                        f"⚠️ [IngestVideoDataUseCase] Không thể upload thumbnail lên S3/MinIO ({exc}), dùng URL cục bộ: {final_image_url}"
                    )

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
            id=record_id,
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
