"""ILLMPort protocol."""

from collections.abc import AsyncIterator
from typing import Protocol

from src.core.domain.entities.chat_message import ChatMessage
from src.core.domain.entities.reference_pattern import SimilarVideoContext
from src.core.domain.entities.viral_script import ViralScript
from src.core.domain.value_objects.platform_target import PlatformTarget


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
