"""Video RAG use cases package."""

from .chat_with_viral_assistant import (
    ChatStreamChunk,
    ChatTurnResult,
    ChatWithViralAssistantUseCase,
)
from .generate_viral_script import GenerateViralScriptUseCase
from .ingest_video_data import IngestVideoDataUseCase, IngestionResult
from .search_viral_patterns import SearchViralPatternsUseCase

__all__ = [
    "IngestVideoDataUseCase",
    "IngestionResult",
    "SearchViralPatternsUseCase",
    "GenerateViralScriptUseCase",
    "ChatWithViralAssistantUseCase",
    "ChatStreamChunk",
    "ChatTurnResult",
]
