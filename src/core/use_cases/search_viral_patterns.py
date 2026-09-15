"""SearchViralPatternsUseCase implementation."""

from src.core.domain.entities.reference_pattern import SimilarVideoContext
from src.core.ports.embedding_port import IEmbeddingPort
from src.core.ports.vector_store_port import IVectorStorePort


class SearchViralPatternsUseCase:
    """Performs semantic similarity search for viral patterns in the vector store."""

    def __init__(
        self,
        embedding_port: IEmbeddingPort,
        vector_store_port: IVectorStorePort,
    ) -> None:
        self._embed = embedding_port
        self._vector_store = vector_store_port

    async def execute(self, query: str, top_k: int = 5) -> list[SimilarVideoContext]:
        """Vectorize search query and retrieve top-K matching video contexts."""
        clean_query = query.strip()
        if not clean_query:
            return []

        # 1. Generate query embedding
        query_vector = await self._embed.embed_text(clean_query)

        # 2. Retrieve top-K from vector store
        results = await self._vector_store.search(query_vector=query_vector, top_k=top_k)
        return results
