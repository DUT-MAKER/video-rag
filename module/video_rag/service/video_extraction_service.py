"""VideoExtractionPipelineService implementation.

AI Domain Service that orchestrates technical multimodal extraction:
1. FFmpeg: Audio (.wav) extraction & keyframe extraction.
2. BentoML WhisperX: Speech-to-Text & Speaker Diarization.
3. Vision LLM: Best thumbnail frame selection.
4. Text LLM: Viral caption, summary, and hashtag generation.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from loguru import logger

from module.video_rag.domain.entities.extraction_result import VideoExtractionResult
from module.video_rag.domain.exceptions import DomainValidationError
from module.video_rag.port.llm_port import ILLMPort
from module.video_rag.port.media_extractor_port import IMediaExtractorPort
from module.video_rag.port.thumbnail_selector_port import IThumbnailSelectorPort
from module.video_rag.port.transcriber_port import ITranscriberPort
from module.video_rag.service.video_store_service import VideoStoreService


class VideoExtractionPipelineService:
    """Orchestrates video processing, STT transcription, diarization, and LLM enrichment."""

    def __init__(
        self,
        media_extractor_port: IMediaExtractorPort,
        transcriber_port: ITranscriberPort,
        thumbnail_selector_port: IThumbnailSelectorPort,
        llm_port: ILLMPort,
        video_store_service: VideoStoreService,
    ) -> None:
        self._media = media_extractor_port
        self._transcriber = transcriber_port
        self._thumbnail = thumbnail_selector_port
        self._llm = llm_port
        self._store = video_store_service

    async def execute(
        self,
        video_path: str,
        language: str = "vi",
        enable_diarization: bool = True,
        output_thumbnail_dir: str | None = None,
    ) -> VideoExtractionResult:
        """Execute full extraction pipeline on a video file."""
        if not video_path or not os.path.exists(video_path):
            raise DomainValidationError(f"Video file path is invalid or does not exist: {video_path}")

        temp_work_dir = tempfile.mkdtemp(prefix="extract_video_")
        logger.info(f"📁 [ExtractionPipeline] Tạo thư mục làm việc tạm: {temp_work_dir}")
        try:
            # 1. Extract audio & duration
            temp_audio_path = os.path.join(temp_work_dir, "audio.wav")
            logger.info("🎵 [ExtractionPipeline] [1/5] Bắt đầu tách audio (FFmpeg -> 16kHz mono WAV)...")
            await self._media.extract_audio(video_path, temp_audio_path)
            duration = await self._media.get_duration(video_path)
            logger.info(f"✅ [ExtractionPipeline] Đã tách audio thành công. Thời lượng: {duration:.1f}s")

            # 2. Extract candidate keyframes
            temp_frames_dir = os.path.join(temp_work_dir, "frames")
            logger.info("🎞️ [ExtractionPipeline] [2/5] Trích xuất candidate keyframes (mỗi 2.0s)...")
            candidate_frames = await self._media.extract_candidate_frames(
                video_path,
                temp_frames_dir,
                interval_seconds=2.0,
            )
            logger.info(f"✅ [ExtractionPipeline] Trích xuất được {len(candidate_frames)} khung hình")

            # 3. Speech-to-text with speaker diarization
            logger.info(
                f"🎙️ [ExtractionPipeline] [3/5] Gọi BentoML WhisperX STT & Diarization "
                f"(lang='{language}', diarization={enable_diarization})..."
            )
            transcription = await self._transcriber.transcribe(
                temp_audio_path,
                language=language,
                enable_diarization=enable_diarization,
            )
            logger.info(
                f"✅ [ExtractionPipeline] STT hoàn tất! Phát hiện {transcription.speaker_count} speaker(s), "
                f"{len(transcription.segments)} segments. Độ dài transcript: {len(transcription.full_text)} ký tự"
            )

            # 4. Select best thumbnail
            logger.info("🖼️ [ExtractionPipeline] [4/5] Chọn best thumbnail qua Vision AI...")
            best_thumb_temp = await self._thumbnail.select_best_frame(
                candidate_frames,
                video_context=transcription.full_text[:500],
            )

            # Upload selected thumbnail to MinIO via VideoStoreService
            final_thumbnail_path = ""
            if best_thumb_temp and os.path.exists(best_thumb_temp):
                stem = Path(video_path).stem
                try:
                    final_thumbnail_path = await self._store.upload_thumbnail_file(
                        local_image_path=best_thumb_temp,
                        stem=stem,
                    )
                except Exception as s3_err:
                    logger.warning(f"⚠️ [ExtractionPipeline] Không thể tải thumbnail lên MinIO: {s3_err}")
                if not final_thumbnail_path:
                    target_dir = output_thumbnail_dir or os.path.join("data", "storage", "thumbnails")
                    os.makedirs(target_dir, exist_ok=True)
                    final_thumbnail_path = os.path.join(target_dir, f"{stem}_thumb.jpg")
                    shutil.copyfile(best_thumb_temp, final_thumbnail_path)
                    logger.info(f"✅ [ExtractionPipeline] Đã lưu thumbnail tại: {final_thumbnail_path}")

            # 5. Format speaker-labeled transcript
            extraction_result = VideoExtractionResult(
                video_path=video_path,
                transcript=transcription.full_text,
                transcript_with_speakers="",
                transcript_segments=transcription.segments,
                speaker_count=transcription.speaker_count,
                thumbnail_path=final_thumbnail_path,
                duration_seconds=duration,
            )
            speaker_transcript = extraction_result.format_speaker_transcript()
            extraction_result.transcript_with_speakers = (
                speaker_transcript if speaker_transcript else transcription.full_text
            )

            # 6. LLM enrichment (caption, summary, hashtags)
            enrichment_context = (
                extraction_result.transcript_with_speakers
                if extraction_result.transcript_with_speakers
                else extraction_result.transcript
            )
            logger.info("🤖 [ExtractionPipeline] [5/5] Gọi LLM Enrichment (tạo caption, tóm tắt, hashtags)...")
            enrichment = await self._llm.enrich_video_metadata(
                enrichment_context,
                language=language,
            )
            extraction_result.caption = enrichment.get("caption", "")
            extraction_result.summary = enrichment.get("summary", "")
            extraction_result.hashtag = enrichment.get("hashtag", "")
            logger.info(f"✅ [ExtractionPipeline] LLM hoàn tất: caption='{extraction_result.caption[:60]}...'")

            return extraction_result

        finally:
            shutil.rmtree(temp_work_dir, ignore_errors=True)
