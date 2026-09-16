"""Video RAG endpoints: Ingestion, Similarity Search, and Script Generation."""

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, status

from backend.presentation.schemas.response_dtos import (
    CallToActionResponseDTO,
    HookResponseDTO,
    ReferencedPatternResponseDTO,
    SceneResponseDTO,
    SearchPatternItem,
    StandardResponse,
    ViralScriptResponseDTO,
)
from backend.presentation.schemas.video_dtos import (
    GenerateScriptRequestDTO,
    SearchPatternsRequestDTO,
)
from module.video_rag.use_case.generate_viral_script import GenerateViralScriptUseCase
from module.video_rag.use_case.search_viral_patterns import SearchViralPatternsUseCase

router = APIRouter(tags=["Video RAG"])


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
