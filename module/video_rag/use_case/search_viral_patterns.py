"""SearchViralPatternsUseCase implementation."""

from module.video_rag.domain.entities.reference_pattern import SimilarVideoContext
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.rerank_port import IRerankPort
from module.video_rag.port.vector_store_port import IVectorStorePort


class SearchViralPatternsUseCase:
    """Performs semantic similarity search and optional cross-encoder reranking for viral patterns."""

    def __init__(
        self,
        embedding_port: IEmbeddingPort,
        vector_store_port: IVectorStorePort,
        rerank_port: IRerankPort | None = None,
        candidate_k: int = 15,
    ) -> None:
        self._embed = embedding_port
        self._vector_store = vector_store_port
        self._rerank = rerank_port
        self._candidate_k = candidate_k

    async def execute(
        self,
        query: str,
        top_k: int = 5,
        use_rerank: bool = True,
    ) -> list[SimilarVideoContext]:
        """Vectorize search query, retrieve candidates, and optionally rerank."""
        clean_query = query.strip()
        if not clean_query:
            return []

        # 1. Generate query embedding
        if hasattr(self._embed, "embed_text"):
            query_vector = await self._embed.embed_text(clean_query)
        else:
            query_vector = await self._embed.get_embedding(clean_query)

        # 2. Retrieve candidates from vector store
        fetch_k = max(top_k, self._candidate_k) if (self._rerank and use_rerank) else top_k
        candidates = await self._vector_store.search(query_vector=query_vector, top_k=fetch_k)

        # 3. Optional Reranking
        if self._rerank and use_rerank and candidates:
            candidate_docs = [
                f"Caption: {ctx.caption}\nHook: {ctx.hook_candidate}\nSummary: {ctx.summary}\n{ctx.document}"
                for ctx in candidates
            ]
            ranked_items = await self._rerank.rerank(
                query=clean_query,
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

        return candidates[:top_k]

