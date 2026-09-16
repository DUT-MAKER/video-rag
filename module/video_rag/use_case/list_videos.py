"""ListVideosUseCase implementation."""

from dataclasses import dataclass
from typing import Any

from module.video_rag.port.vector_store_port import IVectorStorePort


@dataclass
class VideoSummaryItem:
    """Summary item of an ingested video for listing."""

    id: str
    caption: str
    hashtag: str
    image_url: str
    video_url: str
    summary: str
    hook_candidate: str
    speaker_count: int = 1
    duration_seconds: float = 0.0


@dataclass
class ListVideosResult:
    """Result of listing video records."""

    items: list[VideoSummaryItem]
    total: int
    limit: int
    offset: int


class ListVideosUseCase:
    """Use case to retrieve a paginated list of all indexed videos from vector store."""

    def __init__(self, vector_store: IVectorStorePort) -> None:
        self._vector_store = vector_store

    async def execute(
        self,
        limit: int = 50,
        offset: int = 0,
        search_query: str = "",
    ) -> ListVideosResult:
        """Execute video listing with optional keyword filtering."""
        records, total = await self._vector_store.list_all(limit=limit, offset=offset)

        items: list[VideoSummaryItem] = []
        for rec in records:
            meta = rec.get("metadata", {})
            caption = meta.get("caption", "")
            hashtag = meta.get("hashtag", "")
            summary = meta.get("summary", "")
            image_url = meta.get("image_url", "")
            video_url = meta.get("video_url", "")
            hook = meta.get("hook_candidate", "")
            speakers = int(meta.get("speaker_count", 1))
            duration = float(meta.get("duration_seconds", 0.0))

            if search_query:
                q = search_query.lower()
                text_to_search = f"{caption} {hashtag} {summary}".lower()
                if q not in text_to_search:
                    continue

            items.append(
                VideoSummaryItem(
                    id=rec["id"],
                    caption=caption,
                    hashtag=hashtag,
                    image_url=image_url,
                    video_url=video_url,
                    summary=summary,
                    hook_candidate=hook,
                    speaker_count=speakers,
                    duration_seconds=duration,
                )
            )

        return ListVideosResult(
            items=items,
            total=total if not search_query else len(items),
            limit=limit,
            offset=offset,
        )
