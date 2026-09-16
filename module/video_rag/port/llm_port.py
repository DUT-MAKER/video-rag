"""ILLMPort protocol."""

from collections.abc import AsyncIterator
from typing import Protocol

from module.video_rag.domain.entities.chat_message import ChatMessage
from module.video_rag.domain.entities.reference_pattern import SimilarVideoContext
from module.video_rag.domain.entities.viral_script import ViralScript
from module.video_rag.domain.value_objects.chat_intent import ChatIntent
from module.video_rag.domain.value_objects.platform_target import PlatformTarget


class ILLMPort(Protocol):
    """Protocol for LLM interactions: generating structured viral scripts and streaming chat responses."""

    async def generate_script(
        self,
        topic: str,
        target_audience: str,
        duration_seconds: int,
        platform: PlatformTarget,
        hook_style: str | None,
        reference_contexts: list[SimilarVideoContext],
    ) -> ViralScript:
        """Submit augmented prompt to LLM and receive structured ViralScript entity."""
        ...

    def stream_chat(
        self,
        messages: list[ChatMessage],
        reference_contexts: list[SimilarVideoContext],
        current_script_json: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream conversational responses chunk by chunk via an async iterator."""
        ...

    async def classify_intent(self, message: str) -> ChatIntent:
        """Classify user query intent into ChatIntent using LLM."""
        ...
    async def enrich_video_metadata(
        self,
        transcript: str,
        language: str = "vi",
    ) -> dict[str, str]:
        """Generate caption, summary, and hashtags from a speaker-labeled transcript.

        The transcript includes speaker labels (e.g., SPEAKER_00, SPEAKER_01)
        which should be used to understand dialogue flow.

        Returns:
            {"caption": "...", "summary": "...", "hashtag": "..."}
        """
        ...

