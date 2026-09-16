"""ChatIntent enumeration."""

from enum import Enum


class ChatIntent(str, Enum):
    """Classified user intent in chatbot conversation."""

    GENERAL_CHAT = "general_chat"
    GENERATE_SCRIPT = "generate_script"
