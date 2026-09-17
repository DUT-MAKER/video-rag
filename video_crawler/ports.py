"""Ports used by the crawler application service."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol
from uuid import UUID

from .domain import CrawlJobRequest, CrawledVideo, DiscoveredVideo, LeasedJob, MediaArtifact, Platform


class PlatformCrawler(Protocol):
    platform: Platform

    async def discover(self, request: CrawlJobRequest) -> AsyncIterator[DiscoveredVideo]: ...


class MediaResolver(Protocol):
    async def resolve(self, video: DiscoveredVideo) -> MediaArtifact: ...

    async def cleanup(self, artifact: MediaArtifact) -> None: ...


class ObjectStorage(Protocol):
    async def store(self, video: DiscoveredVideo, artifact: MediaArtifact) -> tuple[str, str]: ...


class CrawlerRepositoryPort(Protocol):
    async def create_job(self, request: CrawlJobRequest) -> UUID: ...

    async def lease_job(self, owner: str) -> LeasedJob | None: ...

    async def find_video(self, platform: Platform, platform_video_id: str, canonical_url: str) -> bool: ...

    async def save_video(self, job_id: UUID, video: CrawledVideo) -> UUID | None: ...

    async def record_result(self, job_id: UUID, result: str, reason: str | None = None) -> None: ...

    async def finish_job(self, job_id: UUID, failed: bool = False) -> None: ...

    async def fail_job(self, job_id: UUID, detail: str) -> None: ...
