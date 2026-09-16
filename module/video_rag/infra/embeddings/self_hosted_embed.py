"""SelfHostedEmbeddingAdapter implementation."""

import logging

import httpx

from module.video_rag.domain.exceptions import EmbeddingError
from module.video_rag.port.embedding_port import IEmbeddingPort

logger = logging.getLogger(__name__)


class SelfHostedEmbeddingAdapter(IEmbeddingPort):
    """Adapter for connecting to Self-hosted Embedding API (/v1/embeddings)."""

    def __init__(
        self,
        api_base_url: str = "http://localhost:8000/v1",
        api_key: str | None = None,
        model_name: str = "default-embed",
        dimension: int = 384,
        timeout: float = 30.0,
    ) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._api_key = api_key
        self._model_name = model_name
        self._dimension = dimension
        self._timeout = timeout

    async def get_embedding(self, text: str) -> list[float]:
        """Compute embedding vector for a single text."""
        return await self.embed_text(text)

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Compute embedding vectors for a batch of text documents."""
        return await self.embed_batch(texts)

    async def embed_text(self, text: str) -> list[float]:
        """Generate vector embedding for a single text."""
        batch_result = await self.embed_batch([text])
        if not batch_result:
            raise EmbeddingError(f"Embedding API returned empty result for text: '{text[:50]}...'")
        return batch_result[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate vector embeddings for a batch of texts."""
        if not texts:
            return []

        try:
            headers = {"Content-Type": "application/json"}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            url = f"{self._api_base_url}/embeddings"
            payload = {
                "input": texts,
                "model": self._model_name,
            }

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("data", [])
                    items.sort(key=lambda x: x.get("index", 0))
                    embeddings = [item["embedding"] for item in items if "embedding" in item]
                    if len(embeddings) == len(texts):
                        return embeddings
                    raise EmbeddingError(f"Expected {len(texts)} embeddings, but received {len(embeddings)}.")

                error_msg = f"Embedding service returned HTTP {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise EmbeddingError(error_msg)
        except Exception as exc:
            if isinstance(exc, EmbeddingError):
                raise
            logger.error(f"Failed to generate embeddings: {exc}")
            raise EmbeddingError(f"Failed to generate embeddings from {self._api_base_url}: {exc}") from exc
