"""ChatWithViralAssistantUseCase implementation."""

import json
import logging
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from module.video_rag.domain.entities.chat_session import ChatSession
from module.video_rag.domain.entities.reference_pattern import (
    ReferencedPattern,
    SimilarVideoContext,
)
from module.video_rag.domain.exceptions import DomainValidationError
from module.video_rag.domain.value_objects.chat_intent import ChatIntent
from module.video_rag.domain.value_objects.message_role import MessageRole
from module.video_rag.port.chat_session_store_port import IChatSessionStorePort
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.llm_port import ILLMPort
from module.video_rag.port.rerank_port import IRerankPort
from module.video_rag.port.vector_store_port import IVectorStorePort
from module.video_rag.use_case.tiered_intent_classifier import TieredIntentClassifier

logger = logging.getLogger(__name__)


@dataclass
class ChatStreamChunk:
    """Single token chunk yielded during real-time streaming."""

    session_id: str
    token: str
    is_first: bool = False
    is_done: bool = False
    intent: ChatIntent = ChatIntent.GENERAL_CHAT
    referenced_patterns: list[ReferencedPattern] = field(default_factory=list)


@dataclass
class ChatTurnResult:
    """Non-streaming result of a completed chat turn."""

    session_id: str
    reply: str
    role: MessageRole
    intent: ChatIntent
    referenced_patterns: list[ReferencedPattern]
    created_at: float


class ChatWithViralAssistantUseCase:
    """Orchestrates conversational viral co-pilot interactions.
    1. Loads or initializes the active ChatSession from IChatSessionStorePort.
    2. Analyzes user intent using a 3-tier cascade (Rule-based -> Semantic Embedding -> LLM)
       to determine whether viral benchmark retrieval is needed.
    3. Retrieves top relevant viral patterns via IVectorStorePort when applicable.
    4. Appends user message and streams assistant response via ILLMPort.
    5. Saves updated conversation turn and referenced benchmark patterns.
    """

    def __init__(
        self,
        llm_port: ILLMPort,
        embedding_port: IEmbeddingPort,
        vector_store_port: IVectorStorePort,
        session_store_port: IChatSessionStorePort,
        rerank_port: IRerankPort | None = None,
        candidate_k: int = 15,
        intent_classifier: TieredIntentClassifier | None = None,
    ) -> None:
        self._llm = llm_port
        self._embed = embedding_port
        self._vector_store = vector_store_port
        self._session_store = session_store_port
        self._rerank = rerank_port
        self._candidate_k = candidate_k
        self._classifier = intent_classifier or TieredIntentClassifier(
            embedding_port=self._embed,
            llm_port=self._llm,
        )

    async def _detect_intent(self, message: str) -> ChatIntent:
        """Classify user intent using the 3-tier cascade."""
        intent, tier_name = await self._classifier.classify(message)
        logger.info("Classified intent: %s via tier: %s", intent, tier_name)
        return intent

    def _should_trigger_rag(self, message: str, intent: ChatIntent) -> bool:
        """Determine whether RAG benchmark search should be triggered."""
        return intent == ChatIntent.GENERATE_SCRIPT

    async def _resolve_session(self, session_id: str | None) -> ChatSession:
        """Fetch existing session or create a new session."""
        if session_id:
            existing = await self._session_store.get_session(session_id)
            if existing is not None:
                return existing
            return ChatSession(session_id=session_id)
        return ChatSession()

    async def _retrieve_references(self, query: str, top_k: int = 3) -> list[SimilarVideoContext]:
        """Query vector database for similar benchmark video records with optional reranking."""
        try:
            if hasattr(self._embed, "embed_text"):
                query_vector = await self._embed.embed_text(query)
            else:
                query_vector = await self._embed.get_embedding(query)

            fetch_k = max(top_k, self._candidate_k) if self._rerank else top_k
            candidates = await self._vector_store.search(query_vector=query_vector, top_k=fetch_k)

            if self._rerank and candidates:
                try:
                    candidate_docs = [
                        f"Caption: {ctx.caption}\nHook: {ctx.hook_candidate}\nSummary: {ctx.summary}\n{ctx.document}"
                        for ctx in candidates
                    ]
                    ranked_items = await self._rerank.rerank(
                        query=query,
                        documents=candidate_docs,
                        top_n=top_k,
                    )
                    reranked_contexts: list[SimilarVideoContext] = []
                    for item in ranked_items:
                        if 0 <= item.index < len(candidates):
                            orig = candidates[item.index]
                            reranked_contexts.append(
                                SimilarVideoContext(
                                    id=orig.id,
                                    document=orig.document,
                                    metadata=orig.metadata,
                                    score=item.score,
                                )
                            )
                    return reranked_contexts or candidates[:top_k]
                except Exception as rerank_err:
                    logger.warning(
                        "Reranking in chat failed (%s). Falling back to top vector search candidates.",
                        rerank_err,
                    )
                    return candidates[:top_k]

            return candidates[:top_k]
        except Exception:
            return []

    async def execute_streaming(
        self,
        user_message: str,
        session_id: str | None = None,
        top_k_references: int = 3,
    ) -> AsyncIterator[ChatStreamChunk]:
        """Stream conversational assistant response tokens chunk by chunk."""
        clean_message = user_message.strip()
        if not clean_message:
            raise DomainValidationError("User message cannot be empty.")

        session = await self._resolve_session(session_id)
        intent = await self._detect_intent(clean_message)

        reference_contexts: list[SimilarVideoContext] = []
        referenced_patterns: list[ReferencedPattern] = []

        if self._should_trigger_rag(clean_message, intent):
            reference_contexts = await self._retrieve_references(clean_message, top_k=top_k_references)
            referenced_patterns = [
                ReferencedPattern(
                    original_caption=ctx.caption,
                    matched_hook=ctx.hook_candidate,
                    minio_video_url=ctx.video_url,
                    similarity_score=ctx.score,
                    summary=ctx.summary,
                    image_url=ctx.image_url,
                )
                for ctx in reference_contexts
            ]

        # Append user message to active session
        session.add_user_message(clean_message)

        # 1. Emit metadata chunk with referenced patterns
        yield ChatStreamChunk(
            session_id=session.session_id,
            token="",
            is_first=True,
            is_done=False,
            intent=intent,
            referenced_patterns=referenced_patterns,
        )

        # 2. Stream tokens from LLM
        current_script_json = (
            json.dumps(session.current_script.to_dict(), ensure_ascii=False) if session.current_script else None
        )
        accumulated_chunks: list[str] = []

        stream_gen = self._llm.stream_chat(
            messages=session.get_context_messages(),
            reference_contexts=reference_contexts,
            current_script_json=current_script_json,
        )

        async for token in stream_gen:
            accumulated_chunks.append(token)
            yield ChatStreamChunk(
                session_id=session.session_id,
                token=token,
                is_first=False,
                is_done=False,
                intent=intent,
            )

        # 3. Finalize and persist session turn
        full_reply = "".join(accumulated_chunks)
        session.add_assistant_message(
            content=full_reply,
            references=referenced_patterns,
        )
        await self._session_store.save_session(session)

        # 4. Emit done chunk
        yield ChatStreamChunk(
            session_id=session.session_id,
            token="",
            is_first=False,
            is_done=True,
            intent=intent,
        )

    async def execute_turn(
        self,
        user_message: str,
        session_id: str | None = None,
        top_k_references: int = 3,
    ) -> ChatTurnResult:
        """Execute non-streaming conversational turn."""
        accumulated_tokens: list[str] = []
        first_chunk: ChatStreamChunk | None = None

        async for chunk in self.execute_streaming(
            user_message=user_message,
            session_id=session_id,
            top_k_references=top_k_references,
        ):
            if chunk.is_first:
                first_chunk = chunk
            elif not chunk.is_done:
                accumulated_tokens.append(chunk.token)

        final_session_id = first_chunk.session_id if first_chunk else (session_id or "")
        final_intent = first_chunk.intent if first_chunk else ChatIntent.GENERAL_CHAT
        final_patterns = first_chunk.referenced_patterns if first_chunk else []

        return ChatTurnResult(
            session_id=final_session_id,
            reply="".join(accumulated_tokens),
            role=MessageRole.ASSISTANT,
            intent=final_intent,
            referenced_patterns=final_patterns,
            created_at=time.time(),
        )

    async def get_session(self, session_id: str) -> ChatSession | None:
        """Retrieve a session by its unique ID."""
        return await self._session_store.get_session(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete an existing session."""
        return await self._session_store.delete_session(session_id)

    async def list_sessions(self) -> list[Any]:
        """List active sessions."""
        return await self._session_store.list_sessions()
