"""GenerateViralScriptUseCase implementation."""

from module.video_rag.domain.entities.reference_pattern import (
    ReferencedPattern,
    SimilarVideoContext,
)
from module.video_rag.domain.entities.viral_script import ViralScript
from module.video_rag.domain.exceptions import DomainValidationError
from module.video_rag.domain.value_objects.platform_target import PlatformTarget
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.llm_port import ILLMPort
from module.video_rag.port.rerank_port import IRerankPort
from module.video_rag.port.vector_store_port import IVectorStorePort


class GenerateViralScriptUseCase:
    """Orchestrates RAG-powered viral script generation:
    1. Embeds user topic to retrieve candidate benchmark viral patterns.
    2. Reranks candidates via cross-encoder (IRerankPort) to select top-N relevant patterns.
    3. Builds an augmented context prompt with proven viral formulas.
    4. Calls LLM to generate structured script with 3s hook, storyboard, and AI prompts.
    5. Validates and attaches benchmark references.
    """

    def __init__(
        self,
        llm_port: ILLMPort,
        embedding_port: IEmbeddingPort,
        vector_store_port: IVectorStorePort,
        rerank_port: IRerankPort | None = None,
        candidate_k: int = 15,
    ) -> None:
        self._llm = llm_port
        self._embed = embedding_port
        self._vector_store = vector_store_port
        self._rerank = rerank_port
        self._candidate_k = candidate_k

    async def execute(
        self,
        topic: str,
        target_audience: str = "General social media audience",
        duration_seconds: int = 45,
        platform: PlatformTarget = PlatformTarget.TIKTOK,
        hook_style: str | None = None,
        top_k_patterns: int = 3,
    ) -> ViralScript:
        """Execute RAG generation workflow."""
        clean_topic = topic.strip()
        if not clean_topic:
            raise DomainValidationError("Video topic cannot be empty.")

        if duration_seconds < 15 or duration_seconds > 180:
            raise DomainValidationError("Video duration must be between 15 and 180 seconds.")

        # 1. Compose search query and generate embedding
        search_query = f"Topic: {clean_topic}. Target audience: {target_audience}"
        if hasattr(self._embed, "embed_text"):
            query_vector = await self._embed.embed_text(search_query)
        else:
            query_vector = await self._embed.get_embedding(search_query)

        # 2. Retrieve benchmark patterns from vector store (Stage 1: Vector Search)
        reference_contexts: list[SimilarVideoContext] = []
        try:
            fetch_k = max(top_k_patterns, self._candidate_k) if self._rerank else top_k_patterns
            candidates = await self._vector_store.search(
                query_vector=query_vector,
                top_k=fetch_k,
            )

            # Stage 2: Cross-encoder Reranking
            if self._rerank and candidates:
                candidate_docs = [
                    f"Caption: {ctx.caption}\nHook: {ctx.hook_candidate}\nSummary: {ctx.summary}\n{ctx.document}"
                    for ctx in candidates
                ]
                ranked_items = await self._rerank.rerank(
                    query=clean_topic,
                    documents=candidate_docs,
                    top_n=top_k_patterns,
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
                reference_contexts = reranked_contexts or candidates[:top_k_patterns]
            else:
                reference_contexts = candidates[:top_k_patterns]
        except Exception:
            # If vector store is empty or unavailable, proceed with zero-shot generation
            reference_contexts = []

        # 3. Call LLM to generate viral script
        viral_script = await self._llm.generate_script(
            topic=clean_topic,
            target_audience=target_audience,
            duration_seconds=duration_seconds,
            platform=platform,
            hook_style=hook_style,
            reference_contexts=reference_contexts,
        )

        # 4. Attach retrieved references if not already populated
        if not viral_script.references and reference_contexts:
            viral_script.references = [
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

        return viral_script
