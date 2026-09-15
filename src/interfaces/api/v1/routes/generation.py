"""Generation API route."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.domain.exceptions import DomainValidationError, ScriptGenerationError
from src.core.use_cases.generate_viral_script import GenerateViralScriptUseCase
from src.interfaces.api.dependencies import get_generate_script_use_case
from src.interfaces.schemas.request_dtos import GenerateScriptRequestDTO
from src.interfaces.schemas.response_dtos import (
    CallToActionResponseDTO,
    HookResponseDTO,
    ReferencedPatternResponseDTO,
    SceneResponseDTO,
    StandardResponse,
    ViralScriptResponseDTO,
)

router = APIRouter(tags=["Generation"])


@router.post(
    "/generate-script",
    response_model=StandardResponse[ViralScriptResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Generate complete production-ready viral script (1-Click RAG)",
)
async def generate_viral_script(
    request: GenerateScriptRequestDTO,
    use_case: GenerateViralScriptUseCase = Depends(get_generate_script_use_case),
) -> StandardResponse[ViralScriptResponseDTO]:
    """AI Agent script generation pipeline:
    1. Retrieves relevant high-performing benchmark patterns from knowledge store.
    2. Synthesizes knowledge context into Master Prompt.
    3. Generates 3s retention hook, second-by-second storyboard,
       and generative AI prompts (Midjourney/Flux + Veo/Runway).
    """
    try:
        script = await use_case.execute(
            topic=request.topic,
            target_audience=request.target_audience,
            duration_seconds=request.duration_seconds,
            platform=request.platform,
            hook_style=request.hook_style,
            top_k_patterns=request.top_k_patterns,
        )
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except ScriptGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal script generation error: {e}",
        ) from e

    # Map Domain Entity to Response DTO
    response_data = ViralScriptResponseDTO(
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
        message="Viral script generated successfully.",
        data=response_data,
    )
