"""Core use cases package."""

from src.core.use_cases.chat_with_viral_assistant import (
    ChatStreamChunk,
    ChatTurnResult,
    ChatWithViralAssistantUseCase,
)
from src.core.use_cases.generate_viral_script import GenerateViralScriptUseCase
from src.core.use_cases.ingest_video_data import IngestionResult, IngestVideoDataUseCase
from src.core.use_cases.search_viral_patterns import SearchViralPatternsUseCase

__all__ = [
    "ChatStreamChunk",
    "ChatTurnResult",
    "ChatWithViralAssistantUseCase",
    "IngestVideoDataUseCase",
    "IngestionResult",
    "SearchViralPatternsUseCase",
    "GenerateViralScriptUseCase",
]
