"""TieredIntentClassifier: 3-tier cascade intent detection (Rule-based -> Semantic Embedding -> LLM)."""

import logging
import math
from typing import Sequence

from module.video_rag.domain.value_objects.chat_intent import ChatIntent
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.llm_port import ILLMPort

logger = logging.getLogger(__name__)


def _cosine_similarity(v1: Sequence[float], v2: Sequence[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    dot = sum(a * b for a, b in zip(v1, v2, strict=False))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)


class TieredIntentClassifier:
    """Cascade 3-tier intent classifier:
    1. Tier 1 (Rule-Based): Fast heuristics for high-confidence explicit phrases (0ms).
    2. Tier 2 (Semantic Embedding): Cosine similarity against exemplar centroids (10-20ms).
    3. Tier 3 (LLM): Few-shot/zero-shot structured classification for ambiguous boundaries (~200-400ms).
    """

    GENERATE_SCRIPT_ANCHORS: list[str] = [
        "Tư vấn cho mình cách làm một clip viral thu hút người xem",
        "Làm sao để giữ chân khán giả ở 3 giây đầu tiên và tối ưu retention",
        "Gợi ý ý tưởng nội dung và kịch bản cho video ngắn",
        "Xây dựng cốt truyện, phân cảnh và hình ảnh cho video TikTok",
        "Draft a viral short video script with strong hook and visual storyboard",
        "Generate image and video generation prompts for each scene in the script",
    ]

    GENERAL_CHAT_ANCHORS: list[str] = [
        "Trò chuyện giải đáp kiến thức và thông tin nói chung",
        "Tâm sự, hỏi thăm sức khỏe, công việc và cuộc sống hàng ngày",
        "Hỏi về thông tin thời sự, thời tiết hoặc đời sống tổng quát",
        "Casual conversation, general questions and daily chit chat",
    ]

    # Tier 1 High-confidence compound phrases
    HIGH_CONFIDENCE_SCRIPT_PHRASES: list[str] = [
        "viết kịch bản",
        "tạo kịch bản",
        "lên kịch bản",
        "soạn kịch bản",
        "làm kịch bản",
        "sinh kịch bản",
        "draft script",
        "write script",
        "generate script",
        "sửa cảnh",
        "chỉnh sửa cảnh",
        "phân cảnh",
        "viết hook",
        "tạo hook",
        "hook video",
        "tạo prompt",
        "image prompt",
        "video prompt",
    ]

    # Tier 1 High-confidence greetings & pure chit-chat (exact lower stripped match)
    HIGH_CONFIDENCE_GREETINGS: set[str] = {
        "hi",
        "hello",
        "xin chào",
        "chào bạn",
        "chào bot",
        "chào",
        "alo",
        "hey",
        "cảm ơn",
        "cám ơn",
        "thanks",
        "thank you",
        "tạm biệt",
        "bạn là ai",
        "who are you",
    }

    def __init__(
        self,
        embedding_port: IEmbeddingPort,
        llm_port: ILLMPort,
        similarity_threshold: float = 0.70,
        similarity_margin: float = 0.08,
    ) -> None:
        self._embedding = embedding_port
        self._llm = llm_port
        self._threshold = similarity_threshold
        self._margin = similarity_margin
        self._script_anchor_vectors: list[list[float]] | None = None
        self._chat_anchor_vectors: list[list[float]] | None = None

    def _classify_tier1(self, message: str) -> ChatIntent | None:
        """Tier 1: Fast rule-based heuristics."""
        lower = message.lower().strip()

        # Check explicit high-confidence script phrases first
        if any(phrase in lower for phrase in self.HIGH_CONFIDENCE_SCRIPT_PHRASES):
            return ChatIntent.GENERATE_SCRIPT

        # Check explicit greetings with no script keywords
        if any(g in lower for g in self.HIGH_CONFIDENCE_GREETINGS):
            return ChatIntent.GENERAL_CHAT

        return None

    async def _ensure_anchor_vectors(self) -> None:
        """Lazily initialize anchor vector embeddings."""
        if self._script_anchor_vectors is not None and self._chat_anchor_vectors is not None:
            return

        all_anchors = self.GENERATE_SCRIPT_ANCHORS + self.GENERAL_CHAT_ANCHORS
        if hasattr(self._embedding, "embed_batch"):
            all_vectors = await self._embedding.embed_batch(all_anchors)
        else:
            all_vectors = [await self._embedding.embed_text(a) for a in all_anchors]

        split_idx = len(self.GENERATE_SCRIPT_ANCHORS)
        self._script_anchor_vectors = all_vectors[:split_idx]
        self._chat_anchor_vectors = all_vectors[split_idx:]

    async def _classify_tier2(
        self,
        query_vector: list[float],
    ) -> tuple[ChatIntent | None, float, float]:
        """Tier 2: Semantic embedding comparison against exemplar vectors."""
        await self._ensure_anchor_vectors()
        assert self._script_anchor_vectors is not None
        assert self._chat_anchor_vectors is not None

        score_script = max(_cosine_similarity(query_vector, anchor_vec) for anchor_vec in self._script_anchor_vectors)
        score_chat = max(_cosine_similarity(query_vector, anchor_vec) for anchor_vec in self._chat_anchor_vectors)

        # Clear winner with high confidence
        if score_script >= self._threshold and (score_script - score_chat) >= self._margin:
            return ChatIntent.GENERATE_SCRIPT, score_script, score_chat

        if score_chat >= self._threshold and (score_chat - score_script) >= self._margin:
            return ChatIntent.GENERAL_CHAT, score_script, score_chat

        # Ambiguous boundary -> Needs Tier 3
        return None, score_script, score_chat

    async def classify(self, message: str) -> tuple[ChatIntent, str]:
        """Classify user intent across 3 cascading tiers.
        Returns:
            tuple[ChatIntent, str]: (classified_intent, deciding_tier)
        """
        clean_msg = message.strip()
        if not clean_msg:
            return ChatIntent.GENERAL_CHAT, "rule_based"

        # --- Tier 1: Rule-based heuristics (~0ms) ---
        tier1_intent = self._classify_tier1(clean_msg)
        if tier1_intent is not None:
            return tier1_intent, "rule_based"

        # --- Tier 2: Semantic embedding router (~10-20ms) ---
        try:
            if hasattr(self._embedding, "embed_text"):
                query_vec = await self._embedding.embed_text(clean_msg)
            else:
                query_vec = await self._embedding.get_embedding(clean_msg)

            tier2_intent, score_script, score_chat = await self._classify_tier2(query_vec)
            if tier2_intent is not None:
                return tier2_intent, "semantic_embedding"
        except Exception as err:
            logger.warning("Tier 2 embedding router failed, proceeding to Tier 3: %s", err)
            score_script, score_chat = 0.5, 0.5

        # --- Tier 3: LLM structured classifier (~200-400ms) ---
        try:
            llm_intent = await self._llm.classify_intent(clean_msg)
            return llm_intent, "llm"
        except Exception as err:
            logger.warning("Tier 3 LLM classification failed, falling back to top embedding score: %s", err)
            fallback_intent = ChatIntent.GENERATE_SCRIPT if score_script >= score_chat else ChatIntent.GENERAL_CHAT
            return fallback_intent, "semantic_embedding_fallback"
