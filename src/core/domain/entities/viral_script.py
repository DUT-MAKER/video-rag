"""ViralScript, Hook, Scene, and CallToAction entities."""

from dataclasses import dataclass, field
from typing import Any

from src.core.domain.entities.reference_pattern import ReferencedPattern
from src.core.domain.value_objects.hook_type import HookType
from src.core.domain.value_objects.platform_target import PlatformTarget


@dataclass
class Hook:
    """The critical opening 3-5 seconds that determines viewer retention."""

    hook_type: HookType
    script: str
    visual_action: str
    retention_rationale: str
    duration_seconds: int = 4


@dataclass
class Scene:
    """Detailed storyboard breakdown scene with second-by-second timestamps."""

    scene_number: int
    time_range: str
    narration: str
    visual_action: str
    image_prompt: str
    video_prompt: str
    audio_sfx_cue: str


@dataclass
class CallToAction:
    """Closing call-to-action to maximize engagement (Follow, Save, Share)."""

    script: str
    visual_cue: str


@dataclass
class ViralScript:
    """Complete production-ready viral short-form video script."""

    title: str
    target_niche: str
    platform: PlatformTarget
    target_duration_seconds: int
    hook: Hook
    scenes: list[Scene]
    call_to_action: CallToAction
    references: list[ReferencedPattern] = field(default_factory=list)
    suggested_hashtags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize domain entity to dictionary."""
        return {
            "title": self.title,
            "target_niche": self.target_niche,
            "platform": self.platform.value,
            "target_duration_seconds": self.target_duration_seconds,
            "hook": {
                "hook_type": self.hook.hook_type.value,
                "script": self.hook.script,
                "visual_action": self.hook.visual_action,
                "retention_rationale": self.hook.retention_rationale,
                "duration_seconds": self.hook.duration_seconds,
            },
            "scenes": [
                {
                    "scene_number": s.scene_number,
                    "time_range": s.time_range,
                    "narration": s.narration,
                    "visual_action": s.visual_action,
                    "image_prompt": s.image_prompt,
                    "video_prompt": s.video_prompt,
                    "audio_sfx_cue": s.audio_sfx_cue,
                }
                for s in self.scenes
            ],
            "call_to_action": {
                "script": self.call_to_action.script,
                "visual_cue": self.call_to_action.visual_cue,
            },
            "references": [
                {
                    "original_caption": r.original_caption,
                    "matched_hook": r.matched_hook,
                    "minio_video_url": r.minio_video_url,
                    "similarity_score": r.similarity_score,
                    "summary": r.summary,
                    "image_url": r.image_url,
                }
                for r in self.references
            ],
            "suggested_hashtags": self.suggested_hashtags,
        }
