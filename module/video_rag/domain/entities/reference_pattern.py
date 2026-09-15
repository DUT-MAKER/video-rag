"""ReferencedPattern and SimilarVideoContext entities."""

from dataclasses import dataclass
from typing import Any


@dataclass
class SimilarVideoContext:
    """Retrieved similar video context from the vector database."""

    id: str
    document: str
    metadata: dict[str, Any]
    score: float = 0.0

    @property
    def caption(self) -> str:
        return str(self.metadata.get("caption", ""))

    @property
    def video_url(self) -> str:
        return str(self.metadata.get("video_url", ""))

    @property
    def image_url(self) -> str:
        return str(self.metadata.get("image_url", ""))

    @property
    def hook_candidate(self) -> str:
        return str(self.metadata.get("hook_candidate", ""))

    @property
    def summary(self) -> str:
        return str(self.metadata.get("summary", ""))

    @property
    def hashtag(self) -> str:
        return str(self.metadata.get("hashtag", ""))


@dataclass
class ReferencedPattern:
    """Benchmark viral video pattern referenced in a generated script."""

    original_caption: str
    matched_hook: str
    minio_video_url: str
    similarity_score: float
    summary: str = ""
    image_url: str = ""
