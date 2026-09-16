"""Crawler job administration endpoints."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, HTTPException, Query, status

from backend.presentation.api.deps import AdminUser
from backend.presentation.schemas.crawler_dtos import CreateCrawlJobDTO
from video_crawler.domain import Platform
from video_crawler.infrastructure.repository import CrawlerRepository

router = APIRouter(tags=["Video Crawler"])


@router.post("/crawler/jobs", status_code=status.HTTP_202_ACCEPTED)
@inject
async def create_crawl_job(
    payload: CreateCrawlJobDTO,
    admin: AdminUser,
    repository: FromDishka[CrawlerRepository],
) -> dict[str, str]:
    del admin
    job_id = await repository.create_job(payload.to_domain())
    return {"job_id": str(job_id), "status": "queued"}


@router.get("/crawler/jobs")
@inject
async def list_crawl_jobs(
    admin: AdminUser,
    repository: FromDishka[CrawlerRepository],
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict[str, Any]]:
    del admin
    return await repository.list_jobs(limit)


@router.get("/crawler/jobs/{job_id}")
@inject
async def get_crawl_job(
    job_id: UUID,
    admin: AdminUser,
    repository: FromDishka[CrawlerRepository],
) -> dict[str, Any]:
    del admin
    value = await repository.get_job(job_id)
    if value is None:
        raise HTTPException(status_code=404, detail="Crawl job not found")
    return value


@router.get("/crawler/videos")
@inject
async def list_crawled_videos(
    admin: AdminUser,
    repository: FromDishka[CrawlerRepository],
    platform: Platform | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict[str, Any]]:
    del admin
    return await repository.list_videos(platform=platform, limit=limit)
