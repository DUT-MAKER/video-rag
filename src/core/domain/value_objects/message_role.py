"""MessageRole value object."""

from enum import StrEnum


class MessageRole(StrEnum):
    """Role associated with a chat message."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
