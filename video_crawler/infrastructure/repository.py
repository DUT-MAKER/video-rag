"""PostgreSQL repository for durable crawler jobs and accepted videos."""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from video_crawler.domain import CrawlJobRequest, CrawledVideo, JobStatus, LeasedJob, Platform, utc_now
from video_crawler.infrastructure.models import CrawledVideoModel, CrawlJobModel


class CrawlerRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = session_factory

    async def create_job(self, request: CrawlJobRequest) -> UUID:
        job_id = uuid4()
        timestamp = utc_now()
        async with self._sessions.begin() as session:
            session.add(
                CrawlJobModel(
                    id=job_id,
                    request=request.to_dict(),
                    status=JobStatus.QUEUED.value,
                    created_at=timestamp,
                    updated_at=timestamp,
                )
            )
        return job_id

    async def lease_job(self, owner: str) -> LeasedJob | None:
        timestamp = utc_now()
        async with self._sessions.begin() as session:
            statement = (
                select(CrawlJobModel)
                .where(
                    or_(
                        CrawlJobModel.status == JobStatus.QUEUED.value,
                        (CrawlJobModel.status == JobStatus.RUNNING.value)
                        & (CrawlJobModel.lease_expires_at < timestamp),
                    )
                )
                .order_by(CrawlJobModel.created_at)
                .with_for_update(skip_locked=True)
                .limit(1)
            )
            row = (await session.execute(statement)).scalar_one_or_none()
            if row is None:
                return None
            row.status = JobStatus.RUNNING.value
            row.owner = owner
            row.started_at = row.started_at or timestamp
            row.lease_expires_at = timestamp + timedelta(hours=1)
            row.updated_at = timestamp
            return LeasedJob(id=row.id, request=CrawlJobRequest.from_dict(row.request))

    async def find_video(
        self, platform: Platform, platform_video_id: str, canonical_url: str
    ) -> bool:
        async with self._sessions() as session:
            statement = select(CrawledVideoModel.id).where(
                or_(
                    (CrawledVideoModel.platform == platform.value)
                    & (CrawledVideoModel.platform_video_id == platform_video_id),
                    CrawledVideoModel.canonical_url == canonical_url,
                )
            )
            return (await session.execute(statement)).scalar_one_or_none() is not None

    async def save_video(self, job_id: UUID, video: CrawledVideo) -> UUID:
        timestamp = utc_now()
        values = {
            "id": video.id,
            "job_id": job_id,
            "platform": video.platform.value,
            "platform_video_id": video.platform_video_id,
            "canonical_url": video.canonical_url,
            "caption": video.caption,
            "hashtag": video.hashtag,
            "image_url": video.image_url,
            "video_url": video.video_url,
            "metrics": video.metrics,
            "provenance": video.provenance,
            "quality_warnings": video.quality_warnings,
            "published_at": video.published_at,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        async with self._sessions.begin() as session:
            statement = insert(CrawledVideoModel).values(**values)
            statement = statement.on_conflict_do_update(
                constraint="uq_crawler_video_native",
                set_={key: value for key, value in values.items() if key not in {"id", "created_at"}},
            ).returning(CrawledVideoModel.id)
            return (await session.execute(statement)).scalar_one()

    async def record_result(self, job_id: UUID, result: str, reason: str | None = None) -> None:
        async with self._sessions.begin() as session:
            row = await session.get(CrawlJobModel, job_id, with_for_update=True)
            if row is None:
                return
            if result == "discovered":
                row.discovered_count += 1
            elif result == "accepted":
                row.accepted_count += 1
            elif result == "rejected":
                row.rejected_count += 1
                reasons = dict(row.rejection_reasons)
                reasons[reason or "unknown"] = reasons.get(reason or "unknown", 0) + 1
                row.rejection_reasons = reasons
            row.lease_expires_at = utc_now() + timedelta(hours=1)
            row.updated_at = utc_now()

    async def finish_job(self, job_id: UUID, failed: bool = False) -> None:
        async with self._sessions.begin() as session:
            row = await session.get(CrawlJobModel, job_id, with_for_update=True)
            if row is None:
                return
            if failed:
                row.status = JobStatus.FAILED.value
            elif row.accepted_count and row.rejected_count:
                row.status = JobStatus.PARTIAL.value
            elif row.accepted_count:
                row.status = JobStatus.COMPLETED.value
            else:
                row.status = JobStatus.FAILED.value
            row.finished_at = utc_now()
            row.lease_expires_at = None
            row.updated_at = utc_now()

    async def fail_job(self, job_id: UUID, detail: str) -> None:
        async with self._sessions.begin() as session:
            row = await session.get(CrawlJobModel, job_id, with_for_update=True)
            if row:
                row.error_detail = detail[:2000]
        await self.finish_job(job_id, failed=True)

    async def list_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        async with self._sessions() as session:
            rows = (
                await session.execute(
                    select(CrawlJobModel).order_by(CrawlJobModel.created_at.desc()).limit(limit)
                )
            ).scalars()
            return [self._job_dict(row) for row in rows]

    async def get_job(self, job_id: UUID) -> dict[str, Any] | None:
        async with self._sessions() as session:
            row = await session.get(CrawlJobModel, job_id)
            return self._job_dict(row) if row else None

    async def list_videos(
        self, platform: Platform | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        async with self._sessions() as session:
            statement = select(CrawledVideoModel)
            if platform:
                statement = statement.where(CrawledVideoModel.platform == platform.value)
            rows = (
                await session.execute(
                    statement.order_by(CrawledVideoModel.created_at.desc()).limit(limit)
                )
            ).scalars()
            return [self._video_dict(row) for row in rows]

    @staticmethod
    def _job_dict(row: CrawlJobModel) -> dict[str, Any]:
        return {column.name: getattr(row, column.name) for column in row.__table__.columns}

    @staticmethod
    def _video_dict(row: CrawledVideoModel) -> dict[str, Any]:
        return {column.name: getattr(row, column.name) for column in row.__table__.columns}
