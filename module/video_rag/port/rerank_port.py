"""IRerankPort protocol."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RerankedDocument:
    """Represents a document scored and ranked by a cross-encoder reranker."""

    index: int
    score: float
    text: str


class IRerankPort(Protocol):
    """Protocol for scoring and reranking candidate documents against a query."""

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int = 3,
    ) -> list[RerankedDocument]:
        """Rerank a list of text documents against a query string.

        Args:
            query: The user query or topic to compare against.
            documents: Candidate texts retrieved from vector search.
            top_n: Number of top documents to return.

        Returns:
            List of RerankedDocument sorted descending by relevance score.
        """
        ...
