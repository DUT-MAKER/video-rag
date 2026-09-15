"""ChatIntent value object."""

from enum import StrEnum


class ChatIntent(StrEnum):
    """Categorized user intent within a conversational co-pilot session."""

    BRAINSTORM_HOOKS = "brainstorm_hooks"
    DRAFT_SCRIPT = "draft_script"
    REFINE_SCENE = "refine_scene"
    EXPORT_PROMPTS = "export_prompts"
    GENERAL_CHAT = "general_chat"
