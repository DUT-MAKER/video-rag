"""LLM-backed video summaries with a deterministic local fallback."""

from __future__ import annotations

import logging
import re

import httpx


SUMMARY_API_BASE_URL = "https://llm2.dutai.site/v1"
SUMMARY_MODEL = "ggml-org/gemma-4-e4b-it-GGUF:Q4_0"
MAX_TRANSCRIPT_CHARS = 24_000
LOGGER = logging.getLogger(__name__)


class ExtractiveSummaryProvider:
    async def summarize(self, caption: str, transcript: str) -> str:
        sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", transcript) if item.strip()]
        excerpt = " ".join(sentences[:2]) or transcript.strip()
        return (f"{caption.strip()}. {excerpt}" if caption.strip() else excerpt)[:800].strip()


class LlmSummaryProvider:
    def __init__(
        self,
        api_base_url: str = SUMMARY_API_BASE_URL,
        model: str = SUMMARY_MODEL,
        fallback: ExtractiveSummaryProvider | None = None,
    ) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.model = model
        self.fallback = fallback or ExtractiveSummaryProvider()

    async def summarize(self, caption: str, transcript: str) -> str:
        try:
            summary = await self._generate(caption, transcript)
            if summary:
                return summary[:800].strip()
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
            LOGGER.warning(
                "Summary API failed; using extractive fallback: %s",
                type(error).__name__,
            )
        return await self.fallback.summarize(caption, transcript)

    async def _generate(self, caption: str, transcript: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Summarize the video faithfully in at most two concise sentences. "
                        "Use the same language as the source. Do not invent facts. "
                        "Return only the summary text."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Caption:\n{caption}\n\n"
                        f"Transcript:\n{transcript[:MAX_TRANSCRIPT_CHARS]}"
                    ),
                },
            ],
            "temperature": 0.1,
            "max_tokens": 200,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.api_base_url}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
        return str(response.json()["choices"][0]["message"]["content"]).strip()
