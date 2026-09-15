"""Domain value objects package."""

from src.core.domain.value_objects.chat_intent import ChatIntent
from src.core.domain.value_objects.hook_type import HookType
from src.core.domain.value_objects.message_role import MessageRole
from src.core.domain.value_objects.platform_target import PlatformTarget

__all__ = ["ChatIntent", "HookType", "MessageRole", "PlatformTarget"]
