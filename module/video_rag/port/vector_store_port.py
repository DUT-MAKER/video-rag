"""IVectorStorePort protocol."""

from typing import Any, Protocol

from module.video_rag.domain.entities.reference_pattern import SimilarVideoContext


class IVectorStorePort(Protocol):
    """Protocol for vector indexing and similarity retrieval in a Vector Database."""

    async def upsert(
        self,
        id: str,
        vector: list[float],
        metadata: dict[str, Any],
        document: str,
    ) -> None:
        """Insert or update a single vector with associated metadata and document text."""
        ...

    async def upsert_batch(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        """Insert or update a batch of vectors with associated metadatas and documents."""
        ...

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[SimilarVideoContext]:
        """Retrieve top-K most similar vectors based on similarity metric."""
        ...

    async def count(self) -> int:
        """Return total count of indexed vectors in the store."""
        ...

    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Retrieve paginated list of all indexed video records (id, metadata, document) and total count."""
        ...

    async def get_by_id(self, video_id: str) -> dict[str, Any] | None:
        """Retrieve a single video record by ID (id, metadata, document) without vector embedding."""
        ...

    async def delete_by_id(self, video_id: str) -> bool:
        """Delete an indexed record by its ID."""
        ...
