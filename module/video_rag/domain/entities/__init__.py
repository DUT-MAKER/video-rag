"""Domain entities for video RAG."""

from .chat_message import ChatMessage
from .chat_session import ChatSession
from .reference_pattern import ReferencedPattern, SimilarVideoContext
from .video_record import RawVideoRecord
from .viral_script import CallToAction, Hook, Scene, ViralScript

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
]
