"""Standard API Response DTOs."""

from typing import Generic, TypeVar

from pydantic import BaseModel

from module.video_rag.domain.value_objects.hook_type import HookType
from module.video_rag.domain.value_objects.platform_target import PlatformTarget

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper."""

    success: bool = True
    message: str = "Success"
    data: T


class IngestionResponseData(BaseModel):
    """Payload returned upon successful knowledge ingestion."""

    total_processed: int
    total_indexed: int
    extracted_hooks: list[str]
    indexed_ids: list[str]


class SearchPatternItem(BaseModel):
    """Matched benchmark pattern item from vector search."""

    id: str
    caption: str
    matched_hook: str
    summary: str
    video_url: str
    image_url: str
    similarity_score: float


class HookResponseDTO(BaseModel):
    """Retention hook data for opening 3-5 seconds."""

    hook_type: HookType
    script: str
    visual_action: str
    retention_rationale: str
    duration_seconds: int


class SceneResponseDTO(BaseModel):
    """Individual scene breakdown in storyboard."""

    scene_number: int
    time_range: str
    narration: str
    visual_action: str
    image_prompt: str
    video_prompt: str
    audio_sfx_cue: str


class CallToActionResponseDTO(BaseModel):
    """Closing call to action."""

    script: str
    visual_cue: str


class ReferencedPatternResponseDTO(BaseModel):
    """Benchmark pattern reference details."""

    original_caption: str
    matched_hook: str
    minio_video_url: str
    similarity_score: float
    summary: str
    image_url: str


class ViralScriptResponseDTO(BaseModel):
    """Complete generated viral script payload."""

    title: str
    target_niche: str
    platform: PlatformTarget
    target_duration_seconds: int
    hook: HookResponseDTO
    scenes: list[SceneResponseDTO]
    call_to_action: CallToActionResponseDTO
    references: list[ReferencedPatternResponseDTO]
    suggested_hashtags: list[str]
