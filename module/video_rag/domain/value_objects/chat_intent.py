"""ChatIntent enumeration."""

from enum import Enum


class ChatIntent(str, Enum):
    """Classified user intent in chatbot conversation."""

    GENERAL_CHAT = "general_chat"
    GENERAL_QUERY = "general_query"
    BRAINSTORM_HOOKS = "brainstorm_hooks"
    REFINE_SCENE = "refine_scene"
    REFINE_SCRIPT = "refine_script"
    EXPORT_PROMPTS = "export_prompts"
    DRAFT_SCRIPT = "draft_script"
    REQUEST_NEW_SCRIPT = "request_new_script"
    CHANGE_HOOK = "change_hook"
    REQUEST_VARIATIONS = "request_variations"
