"""ChatMessage entity."""

import time
from dataclasses import dataclass, field
from typing import Any

from src.core.domain.entities.reference_pattern import ReferencedPattern
from src.core.domain.value_objects.message_role import MessageRole


@dataclass
class ChatMessage:
    """Represents a single message turn in a multi-turn conversation."""

    role: MessageRole
    content: str
    timestamp: float = field(default_factory=time.time)
    referenced_patterns: list[ReferencedPattern] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize message to dictionary."""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "referenced_patterns": [
                {
                    "original_caption": r.original_caption,
                    "matched_hook": r.matched_hook,
                    "minio_video_url": r.minio_video_url,
                    "similarity_score": r.similarity_score,
                    "summary": r.summary,
                    "image_url": r.image_url,
                }
                for r in self.referenced_patterns
            ],
        }
