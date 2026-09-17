"""Video RAG endpoints: Ingestion, Similarity Search, and Script Generation."""

import os
import shutil
from pathlib import Path

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, File, Form, UploadFile, status
from loguru import logger

from backend.presentation.schemas.response_dtos import (
    CallToActionResponseDTO,
    HookResponseDTO,
    ReferencedPatternResponseDTO,
    SceneResponseDTO,
    SearchPatternItem,
    StandardResponse,
    TranscriptSegmentResponseDTO,
    VideoDetailResponseDTO,
    VideoFileIngestionResponseData,
    VideoListItemDTO,
    VideoListResponseDTO,
    ViralScriptResponseDTO,
)
from backend.presentation.schemas.video_dtos import (
    GenerateScriptRequestDTO,
    SearchPatternsRequestDTO,
)
from module.video_rag.domain.entities.extraction_result import VideoExtractionResult
from module.video_rag.service.video_store_service import VideoStoreService
from module.video_rag.use_case.generate_viral_script import GenerateViralScriptUseCase
from module.video_rag.use_case.get_video_detail import GetVideoDetailUseCase
from module.video_rag.use_case.ingest_video_data import (
    IngestVideoDataUseCase,
    VideoItemInput,
)
from module.video_rag.use_case.list_videos import ListVideosUseCase
from module.video_rag.use_case.search_viral_patterns import SearchViralPatternsUseCase

router = APIRouter(tags=["Video RAG"])


@router.post(
    "/ingest-video",
    response_model=StandardResponse[VideoFileIngestionResponseData],
    status_code=status.HTTP_200_OK,
    summary="Upload raw video file, extract metadata and ingest into Vector Store",
)
@inject
async def ingest_video_from_file(
    use_case: FromDishka[IngestVideoDataUseCase],
    video_store: FromDishka[VideoStoreService],
    file: UploadFile = File(..., description="Video/Audio file to upload and ingest"),
    caption: str = Form(default=""),
    hashtag: str = Form(default=""),
    language: str = Form(default="vi"),
) -> StandardResponse[VideoFileIngestionResponseData]:
    """Upload video/audio file directly, extract metadata (WhisperX STT,
    Diarization, Vision, LLM) and index directly into Vector Store.
    """
    filename = file.filename or "video.mp4"
    logger.info(
        f"🚀 [API] Nhận request ingest video: '{filename}', size: {file.size or 'unknown'} bytes, lang: '{language}'"
    )

    # Save uploaded file to temporary directory
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(filename).suffix or ".mp4"

    temp_path = upload_dir / f"upload_{os.urandom(6).hex()}{suffix}"
    logger.info(f"📥 [API] Lưu file tạm thời vào: {temp_path}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_mb = os.path.getsize(temp_path) / (1024 * 1024)
    logger.info(f"✅ [API] Đã lưu file ({file_size_mb:.2f} MB). Đang upload video async lên MinIO S3...")

    # Upload video file asynchronously to MinIO via VideoStoreService
    minio_video_url = str(temp_path)
    try:
        minio_video_url = await video_store.upload_video_file(
            local_file_path=str(temp_path),
            filename=filename,
        )
        logger.info(f"☁️ [API] Đã upload video lên MinIO thành công: {minio_video_url}")
    except Exception as s3_err:
        logger.warning(f"⚠️ Không thể upload video lên MinIO ({s3_err}), giữ đường dẫn tạm thời.")

    item_input = VideoItemInput(
        video_path=str(temp_path),
        caption=caption,
        hashtag=hashtag,
        language=language,
        video_url=minio_video_url,
    )
    try:
        result = await use_case.execute(input_data=item_input)
    except Exception as e:
        logger.exception(f"❌ [API] Lỗi trong quá trình IngestVideoDataUseCase: {e}")
        raise e
    finally:
        # Clean up temporary uploaded file after extraction completes
        if temp_path.exists():
            try:
                temp_path.unlink()
                logger.info(f"🧹 [API] Đã dọn dẹp file upload tạm: {temp_path}")
            except Exception as clean_err:
                logger.debug(f"Không thể xóa file tạm {temp_path}: {clean_err}")

    extraction = result.latest_extraction or VideoExtractionResult(
        video_path=minio_video_url,
        transcript="",
        transcript_with_speakers="",
    )
    record = result.latest_record

    segments_dto = [
        TranscriptSegmentResponseDTO(
            start=seg.start,
            end=seg.end,
            text=seg.text,
            speaker=seg.speaker,
        )
        for seg in extraction.transcript_segments
    ]

    preview = (
        extraction.transcript_with_speakers[:500]
        if extraction.transcript_with_speakers
        else extraction.transcript[:500]
    )

    logger.info(
        f"🎉 [API] Ingest video thành công! Total indexed: {result.total_indexed}, "
        f"Speakers: {extraction.speaker_count}, Duration: {extraction.duration_seconds:.1f}s"
    )

    return StandardResponse(
        success=True,
        message=f"Successfully extracted metadata and indexed video (speakers: {extraction.speaker_count}).",
        data=VideoFileIngestionResponseData(
            total_indexed=result.total_indexed,
            caption=record.caption if record else extraction.caption,
            summary=record.summary if record else extraction.summary,
            hashtag=record.hashtag if record else extraction.hashtag,
            speaker_count=extraction.speaker_count,
            duration_seconds=extraction.duration_seconds,
            transcript=extraction.transcript,
            transcript_with_speakers=extraction.transcript_with_speakers,
            transcript_preview=preview,
            transcript_segments=segments_dto,
            thumbnail_path=record.image_url if record else extraction.thumbnail_path,
            video_url=record.video_url if record else minio_video_url,
        ),
    )


@router.post(
    "/search",
    response_model=StandardResponse[list[SearchPatternItem]],
    status_code=status.HTTP_200_OK,
    summary="Semantic similarity search over benchmark viral patterns",
)
@router.post(
    "/search-patterns",
    response_model=StandardResponse[list[SearchPatternItem]],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
@inject
async def search_viral_patterns(
    payload: SearchPatternsRequestDTO,
    use_case: FromDishka[SearchViralPatternsUseCase],
) -> StandardResponse[list[SearchPatternItem]]:
    """Retrieve top matching benchmark viral video patterns."""
    contexts = await use_case.execute(query=payload.query, top_k=payload.top_k)

    items = [
        SearchPatternItem(
            id=ctx.id,
            caption=ctx.caption,
            matched_hook=ctx.hook_candidate,
            summary=ctx.summary,
            video_url=ctx.video_url,
            image_url=ctx.image_url,
            similarity_score=ctx.score,
        )
        for ctx in contexts
    ]

    return StandardResponse(
        success=True,
        message=f"Found {len(items)} matching benchmark patterns.",
        data=items,
    )


@router.post(
    "/generate",
    response_model=StandardResponse[ViralScriptResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Generate complete production-ready viral short-form video script with RAG",
)
@router.post(
    "/generate-script",
    response_model=StandardResponse[ViralScriptResponseDTO],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
@inject
async def generate_viral_script(
    payload: GenerateScriptRequestDTO,
    use_case: FromDishka[GenerateViralScriptUseCase],
) -> StandardResponse[ViralScriptResponseDTO]:
    """Execute end-to-end RAG script generation."""
    logger.info(
        f"🎬 [API Generate] Nhận yêu cầu tạo kịch bản video viral từ người dùng:\n"
        f"  - Topic: {payload.topic}\n"
        f"  - Target Audience: {payload.target_audience}\n"
        f"  - Duration: {payload.duration_seconds}s\n"
        f"  - Platform: {payload.platform.value}\n"
        f"  - Hook Style: {payload.hook_style}\n"
        f"  - Top K Patterns: {payload.top_k_patterns}"
    )
    script = await use_case.execute(
        topic=payload.topic,
        target_audience=payload.target_audience,
        duration_seconds=payload.duration_seconds,
        platform=payload.platform,
        hook_style=payload.hook_style,
        top_k_patterns=payload.top_k_patterns,
    )

    data = ViralScriptResponseDTO(
        title=script.title,
        target_niche=script.target_niche,
        platform=script.platform,
        target_duration_seconds=script.target_duration_seconds,
        hook=HookResponseDTO(
            hook_type=script.hook.hook_type,
            script=script.hook.script,
            visual_action=script.hook.visual_action,
            retention_rationale=script.hook.retention_rationale,
            duration_seconds=script.hook.duration_seconds,
        ),
        scenes=[
            SceneResponseDTO(
                scene_number=s.scene_number,
                time_range=s.time_range,
                narration=s.narration,
                visual_action=s.visual_action,
                image_prompt=s.image_prompt,
                video_prompt=s.video_prompt,
                audio_sfx_cue=s.audio_sfx_cue,
            )
            for s in script.scenes
        ],
        call_to_action=CallToActionResponseDTO(
            script=script.call_to_action.script,
            visual_cue=script.call_to_action.visual_cue,
        ),
        references=[
            ReferencedPatternResponseDTO(
                original_caption=r.original_caption,
                matched_hook=r.matched_hook,
                minio_video_url=r.minio_video_url,
                similarity_score=r.similarity_score,
                summary=r.summary,
                image_url=r.image_url,
            )
            for r in script.references
        ],
        suggested_hashtags=script.suggested_hashtags,
    )

    return StandardResponse(
        success=True,
        message="Viral video script generated successfully.",
        data=data,
    )


@router.get(
    "/videos",
    response_model=StandardResponse[VideoListResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="List all indexed viral video records",
)
@inject
async def list_videos(
    use_case: FromDishka[ListVideosUseCase],
    limit: int = 50,
    offset: int = 0,
    search: str = "",
) -> StandardResponse[VideoListResponseDTO]:
    """Retrieve paginated list of all indexed videos."""
    result = await use_case.execute(limit=limit, offset=offset, search_query=search)
    return StandardResponse(
        success=True,
        message=f"Retrieved {len(result.items)} videos (total: {result.total}).",
        data=VideoListResponseDTO(
            items=[
                VideoListItemDTO(
                    id=item.id,
                    caption=item.caption,
                    hashtag=item.hashtag,
                    image_url=item.image_url,
                    video_url=item.video_url,
                    summary=item.summary,
                    hook_candidate=item.hook_candidate,
                    speaker_count=item.speaker_count,
                    duration_seconds=item.duration_seconds,
                )
                for item in result.items
            ],
            total=result.total,
            limit=result.limit,
            offset=result.offset,
        ),
    )


@router.get(
    "/videos/{video_id}",
    response_model=StandardResponse[VideoDetailResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Get full details of an indexed video without id and vector embedding",
)
@inject
async def get_video_detail(
    video_id: str,
    use_case: FromDishka[GetVideoDetailUseCase],
) -> StandardResponse[VideoDetailResponseDTO]:
    """Retrieve full video information excluding internal ID and embedding."""
    detail = await use_case.execute(video_id=video_id)
    if not detail:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found with id '{video_id}'",
        )

    return StandardResponse(
        success=True,
        message="Video details retrieved successfully.",
        data=VideoDetailResponseDTO(
            caption=detail.caption,
            hashtag=detail.hashtag,
            image_url=detail.image_url,
            video_url=detail.video_url,
            summary=detail.summary,
            hook_candidate=detail.hook_candidate,
            transcript=detail.transcript,
            transcript_with_speakers=detail.transcript_with_speakers,
            speaker_count=detail.speaker_count,
            duration_seconds=detail.duration_seconds,
            document=detail.document,
            extra_metadata=detail.extra_metadata,
        ),
    )
