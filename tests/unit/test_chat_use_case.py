"""Unit tests for ChatWithViralAssistantUseCase."""

from collections.abc import AsyncIterator
from typing import Any

import pytest

from module.video_rag.domain.entities.chat_message import ChatMessage
from module.video_rag.domain.entities.chat_session import ChatSession
from module.video_rag.domain.entities.reference_pattern import SimilarVideoContext
from module.video_rag.domain.entities.viral_script import CallToAction, Hook, Scene, ViralScript
from module.video_rag.domain.exceptions import DomainValidationError
from module.video_rag.domain.value_objects.chat_intent import ChatIntent
from module.video_rag.domain.value_objects.hook_type import HookType
from module.video_rag.domain.value_objects.platform_target import PlatformTarget
from module.video_rag.port.chat_session_store_port import IChatSessionStorePort
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.llm_port import ILLMPort
from module.video_rag.port.vector_store_port import IVectorStorePort
from module.video_rag.use_case.chat_with_viral_assistant import ChatWithViralAssistantUseCase


class FakeChatSessionStore(IChatSessionStorePort):
    """Fake in-memory session store for use case unit tests."""

    def __init__(self) -> None:
        self.sessions: dict[str, ChatSession] = {}

    async def get_session(self, session_id: str) -> ChatSession | None:
        return self.sessions.get(session_id)

    async def save_session(self, session: ChatSession) -> None:
        self.sessions[session.session_id] = session

    async def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    async def list_sessions(self) -> list[str]:
        return list(self.sessions.keys())


class FakeLLMPort(ILLMPort):
    """Fake LLM port for testing chat streaming."""

    async def generate_script(
        self,
        topic: str,
        target_audience: str,
        duration_seconds: int,
        platform: PlatformTarget,
        hook_style: str | None,
        reference_contexts: list[SimilarVideoContext],
    ) -> ViralScript:
        return ViralScript(
            title="Fake Title",
            target_niche=target_audience,
            platform=platform,
            target_duration_seconds=duration_seconds,
            hook=Hook(
                hook_type=HookType.PROBLEM_AGITATE,
                script="Fake Hook",
                visual_action="Action",
                retention_rationale="Rationale",
                duration_seconds=4,
            ),
            scenes=[
                Scene(
                    scene_number=1,
                    time_range="00:00 - 00:04",
                    narration="Scene 1",
                    visual_action="Visual 1",
                    image_prompt="Prompt 1",
                    video_prompt="Prompt video",
                    audio_sfx_cue="Cue",
                )
            ],
            call_to_action=CallToAction(script="CTA", visual_cue="Cue"),
        )

    def stream_chat(
        self,
        messages: list[ChatMessage],
        reference_contexts: list[SimilarVideoContext],
        current_script_json: str | None = None,
    ) -> AsyncIterator[str]:
        async def _generator() -> AsyncIterator[str]:
            yield "Here "
            yield "is "
            yield "your "
            yield "viral "
            yield "hook."

        return _generator()

    async def classify_intent(self, message: str) -> ChatIntent:
        lower = message.lower()
        if any(k in lower for k in ["kịch bản", "hook", "cảnh", "video", "script"]):
            return ChatIntent.GENERATE_SCRIPT
        return ChatIntent.GENERAL_CHAT


class FakeEmbeddingPort(IEmbeddingPort):
    """Fake embedding port."""

    async def embed_text(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]

    def get_dimension(self) -> int:
        return 3


class FakeVectorStorePort(IVectorStorePort):
    """Fake vector store with sample benchmark contexts."""

    async def upsert(self, id: str, vector: list[float], metadata: dict[str, Any], document: str) -> None:
        pass

    async def upsert_batch(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        pass

    async def search(self, query_vector: list[float], top_k: int = 5) -> list[SimilarVideoContext]:
        return [
            SimilarVideoContext(
                id="doc_1",
                document="Viral Video 1 document",
                metadata={
                    "caption": "Viral Video 1",
                    "hook_candidate": "Proven viral hook candidate 1",
                    "summary": "Summary of viral video 1",
                    "video_url": "https://minio.example.com/v1.mp4",
                    "image_url": "https://minio.example.com/i1.jpg",
                },
                score=0.95,
            )
        ]

    async def count(self) -> int:
        return 1


@pytest.mark.asyncio
async def test_chat_use_case_turn_execution_and_intent() -> None:
    """Test non-streaming turn execution, RAG trigger, and session creation."""
    session_store = FakeChatSessionStore()
    use_case = ChatWithViralAssistantUseCase(
        llm_port=FakeLLMPort(),
        embedding_port=FakeEmbeddingPort(),
        vector_store_port=FakeVectorStorePort(),
        session_store_port=session_store,
    )

    # Turn with generate script intent -> triggers RAG
    result = await use_case.execute_turn(user_message="Gợi ý hook cho video về thói quen dậy sớm")
    assert result.session_id != ""
    assert result.reply == "Here is your viral hook."
    assert result.intent == ChatIntent.GENERATE_SCRIPT
    assert len(result.referenced_patterns) == 1
    assert result.referenced_patterns[0].matched_hook == "Proven viral hook candidate 1"

    # Verify session was persisted in store
    saved_session = await session_store.get_session(result.session_id)
    assert saved_session is not None
    assert len(saved_session.messages) == 2  # 1 user + 1 assistant
    assert saved_session.messages[0].content == "Gợi ý hook cho video về thói quen dậy sớm"
    assert saved_session.messages[1].content == "Here is your viral hook."

    # Turn with general chat intent -> does not trigger RAG
    res_general = await use_case.execute_turn(user_message="Xin chào, bạn khỏe không?")
    assert res_general.intent == ChatIntent.GENERAL_CHAT
    assert len(res_general.referenced_patterns) == 0


@pytest.mark.asyncio
async def test_chat_use_case_multi_turn_continuation() -> None:
    """Test maintaining context across multiple conversational turns."""
    session_store = FakeChatSessionStore()
    use_case = ChatWithViralAssistantUseCase(
        llm_port=FakeLLMPort(),
        embedding_port=FakeEmbeddingPort(),
        vector_store_port=FakeVectorStorePort(),
        session_store_port=session_store,
    )

    # Turn 1
    res1 = await use_case.execute_turn(user_message="Viết kịch bản video AI")
    session_id = res1.session_id
    assert res1.intent == ChatIntent.GENERATE_SCRIPT

    # Turn 2 with existing session_id
    res2 = await use_case.execute_turn(
        user_message="Hãy sửa cảnh 2 để kịch tính hơn",
        session_id=session_id,
    )
    assert res2.session_id == session_id
    assert res2.intent == ChatIntent.GENERATE_SCRIPT

    # Verify 4 messages accumulated
    saved_session = await session_store.get_session(session_id)
    assert saved_session is not None
    assert len(saved_session.messages) == 4


@pytest.mark.asyncio
async def test_chat_use_case_streaming_flow() -> None:
    """Test streaming chunks emission including metadata, tokens, and done signal."""
    session_store = FakeChatSessionStore()
    use_case = ChatWithViralAssistantUseCase(
        llm_port=FakeLLMPort(),
        embedding_port=FakeEmbeddingPort(),
        vector_store_port=FakeVectorStorePort(),
        session_store_port=session_store,
    )

    chunks = []
    async for chunk in use_case.execute_streaming(user_message="Tạo video viral TikTok"):
        chunks.append(chunk)

    # Chunk 0: metadata
    assert chunks[0].is_first is True
    assert len(chunks[0].referenced_patterns) == 1

    # Middle chunks: tokens
    tokens = [c.token for c in chunks if not c.is_first and not c.is_done]
    assert "".join(tokens) == "Here is your viral hook."

    # Last chunk: done
    assert chunks[-1].is_done is True


@pytest.mark.asyncio
async def test_chat_use_case_validation() -> None:
    """Test validation error on empty message."""
    use_case = ChatWithViralAssistantUseCase(
        llm_port=FakeLLMPort(),
        embedding_port=FakeEmbeddingPort(),
        vector_store_port=FakeVectorStorePort(),
        session_store_port=FakeChatSessionStore(),
    )

    with pytest.raises(DomainValidationError):
        await use_case.execute_turn(user_message="   ")
