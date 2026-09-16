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


class TranscriptSegmentResponseDTO(BaseModel):
    """Timestamped segment with attributed speaker."""

    start: float
    end: float
    text: str
    speaker: str


class VideoFileIngestionResponseData(BaseModel):
    """Payload returned upon successful video file extraction and ingestion."""

    total_indexed: int
    caption: str
    summary: str
    hashtag: str
    speaker_count: int
    duration_seconds: float = 0.0
    transcript: str = ""
    transcript_with_speakers: str = ""
    transcript_preview: str = ""
    transcript_segments: list[TranscriptSegmentResponseDTO] = []
    thumbnail_path: str
    video_url: str



class VideoListItemDTO(BaseModel):
    """Summary representation of a video in list view."""

    id: str
    caption: str
    hashtag: str
    image_url: str
    video_url: str
    summary: str
    hook_candidate: str
    speaker_count: int = 1
    duration_seconds: float = 0.0


class VideoListResponseDTO(BaseModel):
    """Paginated list of videos."""

    items: list[VideoListItemDTO]
    total: int
    limit: int
    offset: int


class VideoDetailResponseDTO(BaseModel):
    """Comprehensive video detail view without internal ID or vector embedding."""

    caption: str
    hashtag: str
    image_url: str
    video_url: str
    summary: str
    hook_candidate: str
    transcript: str
    transcript_with_speakers: str
    speaker_count: int = 1
    duration_seconds: float = 0.0
    document: str = ""
    extra_metadata: dict = {}


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
