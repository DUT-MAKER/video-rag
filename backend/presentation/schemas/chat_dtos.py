"""Chat Request and Response DTOs."""

from typing import Any
from pydantic import BaseModel, Field

from module.video_rag.domain.value_objects.chat_intent import ChatIntent
from module.video_rag.domain.value_objects.message_role import MessageRole
from backend.presentation.schemas.response_dtos import ReferencedPatternResponseDTO


class ChatRequestDTO(BaseModel):
    """Request payload for conversational chat turn or streaming."""

    message: str = Field(..., min_length=1, description="User prompt or message")
    session_id: str | None = Field(default=None, description="Optional existing session ID to resume")
    top_k_references: int = Field(default=3, ge=1, le=10, description="Max benchmark viral patterns to retrieve")


class ChatMessageResponseDTO(BaseModel):
    """Single message turn in a session."""

    role: MessageRole
    content: str
    timestamp: float
    referenced_patterns: list[ReferencedPatternResponseDTO] = Field(default_factory=list)


class ChatResponseDTO(BaseModel):
    """Response payload for non-streaming conversational chat turn."""

    session_id: str
    reply: str
    role: MessageRole
    intent: ChatIntent
    referenced_patterns: list[ReferencedPatternResponseDTO] = Field(default_factory=list)
    created_at: float


class SessionDetailResponseDTO(BaseModel):
    """Detailed chat session history."""

    session_id: str
    message_count: int
    created_at: float
    updated_at: float
    messages: list[ChatMessageResponseDTO]
    current_script: dict[str, Any] | None = None


class SessionListResponseDTO(BaseModel):
    """List of all active conversation sessions."""

    total_sessions: int
    session_ids: list[str]
