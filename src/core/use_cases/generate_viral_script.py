"""GenerateViralScriptUseCase implementation."""

from src.core.domain.entities.reference_pattern import ReferencedPattern, SimilarVideoContext
from src.core.domain.entities.viral_script import ViralScript
from src.core.domain.exceptions import DomainValidationError
from src.core.domain.value_objects.platform_target import PlatformTarget
from src.core.ports.embedding_port import IEmbeddingPort
from src.core.ports.llm_port import ILLMPort
from src.core.ports.vector_store_port import IVectorStorePort


class GenerateViralScriptUseCase:
    """Orchestrates RAG-powered viral script generation:
    1. Embeds user topic to retrieve top benchmark viral video patterns from the knowledge store.
    2. Builds an augmented context prompt with proven formulas.
    3. Calls LLM to generate structured script with 3s hook, storyboard, and AI prompts.
    4. Validates and attaches benchmark references.
    """

    def __init__(
        self,
        llm_port: ILLMPort,
        embedding_port: IEmbeddingPort,
        vector_store_port: IVectorStorePort,
    ) -> None:
        self._llm = llm_port
        self._embed = embedding_port
        self._vector_store = vector_store_port

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
        query_vector = await self._embed.embed_text(search_query)

        # 2. Retrieve benchmark patterns from vector store
        reference_contexts: list[SimilarVideoContext] = []
        try:
            reference_contexts = await self._vector_store.search(
                query_vector=query_vector,
                top_k=top_k_patterns,
            )
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
