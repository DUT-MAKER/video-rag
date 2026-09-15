"""IEmbeddingPort protocol."""

from typing import Protocol


class IEmbeddingPort(Protocol):
    """Protocol for generating vector embeddings from text."""

    async def embed_text(self, text: str) -> list[float]:
        """Generate vector embedding for a single text string."""
        ...

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate vector embeddings for a batch of text strings."""
        ...
