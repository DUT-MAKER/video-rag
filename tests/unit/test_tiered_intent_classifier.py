"""Unit tests for TieredIntentClassifier."""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock

import pytest

from module.video_rag.domain.entities.viral_script import ViralScript
from module.video_rag.domain.value_objects.chat_intent import ChatIntent
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.llm_port import ILLMPort
from module.video_rag.use_case.tiered_intent_classifier import (
    TieredIntentClassifier,
    _cosine_similarity,
)


class MockEmbeddingPort(IEmbeddingPort):
    """Mock embedding port returning controllable vectors."""

    def __init__(self, default_vector: list[float] | None = None) -> None:
        self.default_vector = default_vector or [1.0, 0.0, 0.0]
        self.custom_map: dict[str, list[float]] = {}

    async def embed_text(self, text: str) -> list[float]:
        return self.custom_map.get(text, self.default_vector)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.custom_map.get(t, self.default_vector) for t in texts]

    def get_dimension(self) -> int:
        return len(self.default_vector)


class MockLLMPort(ILLMPort):
    """Mock LLM port."""

    def __init__(self, mock_intent: ChatIntent = ChatIntent.GENERATE_SCRIPT) -> None:
        self.mock_intent = mock_intent
        self.classify_called_with: list[str] = []

    async def generate_script(self, *args: Any, **kwargs: Any) -> ViralScript:
        raise NotImplementedError

    def stream_chat(self, *args: Any, **kwargs: Any) -> AsyncIterator[str]:
        raise NotImplementedError

    async def classify_intent(self, message: str) -> ChatIntent:
        self.classify_called_with.append(message)
        return self.mock_intent


def test_cosine_similarity_edge_cases() -> None:
    """Verify vector cosine math and zero vectors."""
    assert _cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert _cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


@pytest.mark.asyncio
async def test_tier1_rule_based_script_phrases() -> None:
    """Test direct high-confidence script phrases resolve at Tier 1 without calling embedding/LLM."""
    embed = MockEmbeddingPort()
    llm = MockLLMPort()
    classifier = TieredIntentClassifier(embedding_port=embed, llm_port=llm)

    intent, tier = await classifier.classify("Hãy viết kịch bản video TikTok về tài chính")
    assert intent == ChatIntent.GENERATE_SCRIPT
    assert tier == "rule_based"
    assert len(llm.classify_called_with) == 0

    intent2, tier2 = await classifier.classify("Sửa cảnh 2 để ngắn hơn")
    assert intent2 == ChatIntent.GENERATE_SCRIPT
    assert tier2 == "rule_based"

    intent3, tier3 = await classifier.classify("Tạo hook giật gân")
    assert intent3 == ChatIntent.GENERATE_SCRIPT
    assert tier3 == "rule_based"


@pytest.mark.asyncio
async def test_tier1_rule_based_greetings() -> None:
    """Test common greetings resolve to GENERAL_CHAT at Tier 1."""
    embed = MockEmbeddingPort()
    llm = MockLLMPort()
    classifier = TieredIntentClassifier(embedding_port=embed, llm_port=llm)

    for greeting in ["Xin chào", "Hello", "hi", "Cảm ơn bạn", "Bạn là ai"]:
        intent, tier = await classifier.classify(greeting)
        assert intent == ChatIntent.GENERAL_CHAT
        assert tier == "rule_based"

    # Empty message
    empty_intent, empty_tier = await classifier.classify("   ")
    assert empty_intent == ChatIntent.GENERAL_CHAT
    assert empty_tier == "rule_based"


@pytest.mark.asyncio
async def test_tier2_semantic_embedding_router() -> None:
    """Test semantic embedding routing when Tier 1 doesn't match."""
    embed = MockEmbeddingPort()
    # Configure anchors: script anchors along [1.0, 0.0], chat anchors along [0.0, 1.0]
    for anchor in TieredIntentClassifier.GENERATE_SCRIPT_ANCHORS:
        embed.custom_map[anchor] = [1.0, 0.0]
    for anchor in TieredIntentClassifier.GENERAL_CHAT_ANCHORS:
        embed.custom_map[anchor] = [0.0, 1.0]

    llm = MockLLMPort()
    classifier = TieredIntentClassifier(
        embedding_port=embed,
        llm_port=llm,
        similarity_threshold=0.70,
        similarity_margin=0.08,
    )

    # 1. Query vector aligns strongly with script anchor [1.0, 0.0]
    query_script = "Làm sao để người ta xem hết clip này"
    embed.custom_map[query_script] = [0.98, 0.05]

    intent, tier = await classifier.classify(query_script)
    assert intent == ChatIntent.GENERATE_SCRIPT
    assert tier == "semantic_embedding"
    assert len(llm.classify_called_with) == 0

    # 2. Query vector aligns strongly with chat anchor [0.0, 1.0]
    query_chat = "Kể một câu chuyện cười cho mình nghe nhé"
    embed.custom_map[query_chat] = [0.05, 0.98]

    intent2, tier2 = await classifier.classify(query_chat)
    assert intent2 == ChatIntent.GENERAL_CHAT
    assert tier2 == "semantic_embedding"
    assert len(llm.classify_called_with) == 0


@pytest.mark.asyncio
async def test_tier3_llm_classifier_on_ambiguity() -> None:
    """Test fallback to Tier 3 LLM when embedding similarity is ambiguous."""
    embed = MockEmbeddingPort()
    # Both script and chat anchors given equal orthogonal directions
    for anchor in TieredIntentClassifier.GENERATE_SCRIPT_ANCHORS:
        embed.custom_map[anchor] = [1.0, 0.0]
    for anchor in TieredIntentClassifier.GENERAL_CHAT_ANCHORS:
        embed.custom_map[anchor] = [0.0, 1.0]

    # Query with equal similarity to both (45 degrees = [0.707, 0.707])
    ambiguous_query = "Tôi đang phân vân không biết nên làm gì tiếp theo"
    embed.custom_map[ambiguous_query] = [0.707, 0.707]

    llm = MockLLMPort(mock_intent=ChatIntent.GENERATE_SCRIPT)
    classifier = TieredIntentClassifier(
        embedding_port=embed,
        llm_port=llm,
        similarity_threshold=0.70,
        similarity_margin=0.10,
    )

    intent, tier = await classifier.classify(ambiguous_query)
    assert intent == ChatIntent.GENERATE_SCRIPT
    assert tier == "llm"
    assert len(llm.classify_called_with) == 1
    assert llm.classify_called_with[0] == ambiguous_query


@pytest.mark.asyncio
async def test_tier3_llm_failure_graceful_fallback() -> None:
    """Test graceful fallback when LLM encounters network/service failure."""
    embed = MockEmbeddingPort()
    for anchor in TieredIntentClassifier.GENERATE_SCRIPT_ANCHORS:
        embed.custom_map[anchor] = [0.6, 0.4]
    for anchor in TieredIntentClassifier.GENERAL_CHAT_ANCHORS:
        embed.custom_map[anchor] = [0.4, 0.6]

    ambiguous_query = "Một câu hỏi không rõ ràng"
    embed.custom_map[ambiguous_query] = [0.55, 0.45]

    llm = MockLLMPort()
    llm.classify_intent = AsyncMock(side_effect=RuntimeError("LLM API timeout"))

    classifier = TieredIntentClassifier(
        embedding_port=embed,
        llm_port=llm,
        similarity_threshold=0.80,
        similarity_margin=0.20,
    )

    intent, tier = await classifier.classify(ambiguous_query)
    assert intent in (ChatIntent.GENERATE_SCRIPT, ChatIntent.GENERAL_CHAT)
    assert tier == "semantic_embedding_fallback"
