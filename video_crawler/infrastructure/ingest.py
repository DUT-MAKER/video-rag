"""Internal HTTP adapter that hands accepted records to the RAG backend."""

import httpx

from video_crawler.config import CrawlerSettings
from video_crawler.domain import CrawledVideo


class HttpRagIngestor:
    def __init__(self, settings: CrawlerSettings) -> None:
        self.settings = settings

    async def ingest(self, video: CrawledVideo) -> None:
        if not self.settings.internal_token:
            raise RuntimeError("CRAWLER_INTERNAL_TOKEN is not configured")
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                self.settings.ingest_url,
                json={"record": video.to_rag_record()},
                headers={"X-Crawler-Token": self.settings.internal_token},
            )
            response.raise_for_status()
