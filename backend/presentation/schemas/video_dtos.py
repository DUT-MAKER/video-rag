"""Video Request DTOs."""

from typing import Any

from pydantic import BaseModel, Field

from module.video_rag.domain.value_objects.platform_target import PlatformTarget


class IngestRequestDTO(BaseModel):
    """Request DTO for ingesting viral video knowledge records."""

    file_path: str | None = Field(
        default=None,
        description="Path to JSON file containing video records (e.g. data/samples/sample_viral_videos.json)",
        examples=["data/samples/sample_viral_videos.json"],
    )
    records: list[dict[str, Any]] | None = Field(
        default=None,
        description="Direct list of raw video record objects if passing directly via request body",
    )


class IngestVideoFileRequestDTO(BaseModel):
    """Request DTO for extracting metadata from a raw video file and ingesting it."""

    video_path: str = Field(
        ...,
        description="Path to video file on server disk (e.g. data/samples/sample_video.mp4)",
        examples=["data/samples/sample_video.mp4"],
    )
    caption: str = Field(
        default="",
        description="Pre-defined or initial caption for the video",
    )
    hashtag: str = Field(
        default="",
        description="Pre-defined hashtags (comma or space separated)",
    )
    language: str = Field(
        default="vi",
        description="Spoken language code for STT transcription (vi, en, etc.)",
    )


class SearchPatternsRequestDTO(BaseModel):
    """Request DTO for semantic similarity search over benchmark patterns."""

    query: str = Field(
        ...,
        description="Keywords, topic, or concept to retrieve benchmark patterns for",
        examples=["discipline habit"],
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of similar benchmark patterns to retrieve",
    )


class GenerateScriptRequestDTO(BaseModel):
    """Request DTO for generating complete production-ready viral script."""

    topic: str = Field(
        ...,
        description="Core subject or premise of the short-form video",
        examples=["How to apply the 2-minute rule to beat procrastination"],
    )
    target_audience: str = Field(
        default="Working professionals and students looking to maximize productivity",
        description="Target viewer persona and demographics",
    )
    duration_seconds: int = Field(
        default=45,
        ge=15,
        le=180,
        description="Target video duration in seconds (15s, 30s, 45s, 60s)",
    )
    platform: PlatformTarget = Field(
        default=PlatformTarget.TIKTOK,
        description="Target social platform (tiktok, youtube_shorts, instagram_reels)",
    )
    hook_style: str | None = Field(
        default=None,
        description="Preferred hook formula (problem_agitate, contrarian, curiosity_gap, shocking_fact...)",
    )
    top_k_patterns: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of benchmark patterns to retrieve from knowledge store for RAG grounding",
    )
