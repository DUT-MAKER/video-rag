"""Unit tests for chat domain entities and value objects."""

from src.core.domain.entities.chat_message import ChatMessage
from src.core.domain.entities.chat_session import ChatSession
from src.core.domain.entities.reference_pattern import ReferencedPattern
from src.core.domain.value_objects.chat_intent import ChatIntent
from src.core.domain.value_objects.message_role import MessageRole


def test_chat_message_creation_and_serialization() -> None:
    """Test ChatMessage initialization and dictionary representation."""
    ref = ReferencedPattern(
        original_caption="How to wake up at 5am",
        matched_hook="Do not set 5 alarms, do this instead",
        minio_video_url="https://minio.example.com/videos/5am.mp4",
        similarity_score=0.92,
        summary="Morning routine breakdown",
        image_url="https://minio.example.com/thumbnails/5am.jpg",
    )
    msg = ChatMessage(
        role=MessageRole.ASSISTANT,
        content="Here is a high retention hook for you.",
        referenced_patterns=[ref],
    )

    assert msg.role == MessageRole.ASSISTANT
    assert msg.content == "Here is a high retention hook for you."
    assert len(msg.referenced_patterns) == 1
    assert msg.timestamp > 0

    d = msg.to_dict()
    assert d["role"] == "assistant"
    assert d["content"] == msg.content
    assert len(d["referenced_patterns"]) == 1
    assert d["referenced_patterns"][0]["matched_hook"] == "Do not set 5 alarms, do this instead"


def test_chat_session_lifecycle_and_trimming() -> None:
    """Test ChatSession message appending and context window retrieval."""
    session = ChatSession(session_id="test-session-123", max_history_messages=4)
    assert session.session_id == "test-session-123"
    assert len(session.messages) == 0

    # Add messages
    u1 = session.add_user_message("Hello AI")
    assert u1.role == MessageRole.USER
    assert len(session.messages) == 1

    a1 = session.add_assistant_message("Hi creator!")
    assert a1.role == MessageRole.ASSISTANT
    assert len(session.messages) == 2

    # Verify context window
    context = session.get_context_messages()
    assert len(context) == 2
    assert context[0].content == "Hello AI"
    assert context[1].content == "Hi creator!"

    # Add multiple messages to test trimming
    for i in range(10):
        session.add_user_message(f"User message {i}")
        session.add_assistant_message(f"Assistant reply {i}")

    # Maximum limit is max_history_messages * 2 = 8
    assert len(session.messages) <= 8
    d = session.to_dict()
    assert d["session_id"] == "test-session-123"
    assert d["message_count"] == len(session.messages)


def test_chat_intent_and_roles() -> None:
    """Verify StrEnum values for ChatIntent and MessageRole."""
    assert ChatIntent.BRAINSTORM_HOOKS == "brainstorm_hooks"
    assert ChatIntent.DRAFT_SCRIPT == "draft_script"
    assert ChatIntent.REFINE_SCENE == "refine_scene"
    assert ChatIntent.EXPORT_PROMPTS == "export_prompts"
    assert ChatIntent.GENERAL_CHAT == "general_chat"

    assert MessageRole.SYSTEM == "system"
    assert MessageRole.USER == "user"
    assert MessageRole.ASSISTANT == "assistant"
