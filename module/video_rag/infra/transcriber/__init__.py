"""Transcriber adapters."""

from module.video_rag.infra.transcriber.bento_whisperx_adapter import (
    BentoWhisperXAdapter,
)
from module.video_rag.infra.transcriber.whisperx_adapter import (
    WhisperXTranscriberAdapter,
)

__all__ = ["BentoWhisperXAdapter", "WhisperXTranscriberAdapter"]
