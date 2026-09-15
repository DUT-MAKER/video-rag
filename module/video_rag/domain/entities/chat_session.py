"""ChatSession entity."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from module.video_rag.domain.entities.chat_message import ChatMessage
from module.video_rag.domain.entities.reference_pattern import ReferencedPattern
from module.video_rag.domain.entities.viral_script import ViralScript
from module.video_rag.domain.value_objects.message_role import MessageRole


@dataclass
class ChatSession:
    """Manages multi-turn conversation state and the current viral script draft."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[ChatMessage] = field(default_factory=list)
    current_script: ViralScript | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    max_history_messages: int = 20

    def add_user_message(self, content: str) -> ChatMessage:
        """Append a user message to the conversation."""
        msg = ChatMessage(role=MessageRole.USER, content=content)
        self.messages.append(msg)
        self.updated_at = time.time()
        self._trim_history()
        return msg

    def add_assistant_message(
        self,
        content: str,
        references: list[ReferencedPattern] | None = None,
    ) -> ChatMessage:
        """Append an assistant response to the conversation."""
        msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=content,
            referenced_patterns=references or [],
        )
        self.messages.append(msg)
        self.updated_at = time.time()
        self._trim_history()
        return msg

    def update_script(self, script: ViralScript) -> None:
        """Update the active draft viral script for this session."""
        self.current_script = script
        self.updated_at = time.time()

    def get_context_messages(self) -> list[ChatMessage]:
        """Return the window of messages to be included in the LLM prompt context."""
        return self.messages[-self.max_history_messages :]

    def _trim_history(self) -> None:
        """Retain within maximum history size if overflow occurs."""
        max_limit = self.max_history_messages * 2
        if len(self.messages) > max_limit:
            self.messages = self.messages[-max_limit:]

    def to_dict(self) -> dict[str, Any]:
        """Serialize session to dictionary."""
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [m.to_dict() for m in self.messages],
            "current_script": self.current_script.to_dict() if self.current_script else None,
        }
