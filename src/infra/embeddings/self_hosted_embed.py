"""SelfHostedEmbeddingAdapter implementation."""

import hashlib
import math
import re

import httpx

from src.core.ports.embedding_port import IEmbeddingPort


class SelfHostedEmbeddingAdapter(IEmbeddingPort):
    """Adapter for connecting to Self-hosted Embedding API (/v1/embeddings)."""

    def __init__(
        self,
        api_base_url: str = "http://localhost:8000/v1",
        api_key: str | None = None,
        model_name: str = "default-embed",
        dimension: int = 384,
        timeout: float = 30.0,
        fallback_mode: bool = True,
    ) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._api_key = api_key
        self._model_name = model_name
        self._dimension = dimension
        self._timeout = timeout
        self._fallback_mode = fallback_mode

    def _generate_fallback_vector(self, text: str) -> list[float]:
        """Generate deterministic normalized embedding vector based on token hashing.
        Allows full RAG pipeline and test suites to function offline without a running endpoint.
        """
        vec = [0.0] * self._dimension
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return vec

        for token in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dimension
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    async def embed_text(self, text: str) -> list[float]:
        """Generate vector embedding for a single text."""
        batch_result = await self.embed_batch([text])
        return batch_result[0] if batch_result else [0.0] * self._dimension

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate vector embeddings for a batch of texts."""
        if not texts:
            return []

        # Try calling real embedding API endpoint
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
                    # OpenAI format: data: [{"embedding": [...], "index": 0}, ...]
                    items = data.get("data", [])
                    items.sort(key=lambda x: x.get("index", 0))
                    embeddings = [item["embedding"] for item in items if "embedding" in item]
                    if len(embeddings) == len(texts):
                        return embeddings
        except Exception:
            if not self._fallback_mode:
                raise

        # Fallback mode
        return [self._generate_fallback_vector(t) for t in texts]
