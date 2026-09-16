"""DutAiRerankAdapter implementation connecting to DUT AI TEI Reranking Service."""

import logging
from typing import Any

import httpx

from module.video_rag.domain.exceptions import RerankError
from module.video_rag.port.rerank_port import IRerankPort, RerankedDocument

logger = logging.getLogger(__name__)


class DutAiRerankAdapter(IRerankPort):
    """Adapter for DUT AI Hugging Face TEI Reranking service (/rerank)."""

    def __init__(
        self,
        api_base_url: str = "https://textembedding.dutai.io.vn",
        api_key: str | None = "dutaiclb",
        model_name: str = "BAAI/bge-reranker-v2-m3",
        timeout: float = 15.0,
        max_batch_size: int = 32,
    ) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._api_key = api_key
        self._model_name = model_name
        self._timeout = timeout
        self._max_batch_size = max_batch_size

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int = 3,
    ) -> list[RerankedDocument]:
        """Rerank candidate documents using DUT AI Cross-Encoder endpoint."""
        clean_query = query.strip()
        if not clean_query or not documents:
            return []

        # Enforce recommended maximum batch size (<= 32)
        batch_docs = documents[: self._max_batch_size]

        try:
            headers = {"Content-Type": "application/json"}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            url = f"{self._api_base_url}/rerank"
            payload: dict[str, Any] = {
                "query": clean_query,
                "texts": batch_docs,
                "return_text": True,
                "truncate": True,
            }

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        results = [
                            RerankedDocument(
                                index=int(item["index"]),
                                score=float(item["score"]),
                                text=str(item.get("text", batch_docs[int(item["index"])])),
                            )
                            for item in data
                            if "index" in item and "score" in item
                        ]
                        results.sort(key=lambda x: x.score, reverse=True)
                        return results[:top_n]
                    raise RerankError("Reranker response format invalid: expected JSON array.")

                error_msg = f"DUT AI Rerank service returned HTTP {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise RerankError(error_msg)
        except Exception as exc:
            if isinstance(exc, RerankError):
                raise
            error_detail = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
            logger.error(f"Failed to call DUT AI Rerank service: {error_detail}")
            raise RerankError(f"Failed to call DUT AI Rerank service ({error_detail}).") from exc
