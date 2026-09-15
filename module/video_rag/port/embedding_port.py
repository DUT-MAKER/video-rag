"""IEmbeddingPort protocol."""

from typing import Protocol


class IEmbeddingPort(Protocol):
    """Protocol for computing dense semantic vector embeddings for text."""

    async def get_embedding(self, text: str) -> list[float]:
        """Compute embedding vector for a single text document or query."""
        ...

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Compute embedding vectors for a batch of text documents."""
        ...
