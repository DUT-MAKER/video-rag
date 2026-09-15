"""MessageRole enumeration."""

from enum import Enum


class MessageRole(str, Enum):
    """Conversation participant role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
