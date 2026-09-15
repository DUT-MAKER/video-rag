"""Video RAG domain package."""

from .entities import (
    CallToAction,
    ChatMessage,
    ChatSession,
    Hook,
    RawVideoRecord,
    ReferencedPattern,
    Scene,
    SimilarVideoContext,
    ViralScript,
)
from .exceptions import (
    DomainError,
    DomainValidationError,
    ScriptGenerationError,
    SessionNotFoundError,
    VectorStoreError,
    VideoRecordParsingError,
)
from .value_objects import ChatIntent, HookType, MessageRole, PlatformTarget

__all__ = [
    "RawVideoRecord",
    "SimilarVideoContext",
    "ReferencedPattern",
    "Hook",
    "Scene",
    "CallToAction",
    "ViralScript",
    "ChatMessage",
    "ChatSession",
    "ChatIntent",
    "HookType",
    "MessageRole",
    "PlatformTarget",
    "DomainError",
    "DomainValidationError",
    "VideoRecordParsingError",
    "ScriptGenerationError",
    "VectorStoreError",
    "SessionNotFoundError",
]
