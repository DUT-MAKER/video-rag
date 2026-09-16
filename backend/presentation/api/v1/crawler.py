"""Crawler job administration and worker-only RAG handoff."""

from __future__ import annotations

import secrets
from typing import Any
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Header, HTTPException, Query, status

from backend.presentation.api.deps import AdminUser
from backend.presentation.schemas.crawler_dtos import CreateCrawlJobDTO, InternalCrawlerIngestDTO
from backend.presentation.schemas.response_dtos import IngestionResponseData, StandardResponse
from module.video_rag.use_case.ingest_video_data import IngestVideoDataUseCase
from video_crawler.config import CrawlerSettings
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
    indexed: bool | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict[str, Any]]:
    del admin
    return await repository.list_videos(platform=platform, indexed=indexed, limit=limit)


@router.post(
    "/internal/crawler/ingest",
    response_model=StandardResponse[IngestionResponseData],
    include_in_schema=False,
)
@inject
async def ingest_crawled_video(
    payload: InternalCrawlerIngestDTO,
    use_case: FromDishka[IngestVideoDataUseCase],
    settings: FromDishka[CrawlerSettings],
    x_crawler_token: str = Header(default="", alias="X-Crawler-Token"),
) -> StandardResponse[IngestionResponseData]:
    if not settings.internal_token:
        raise HTTPException(status_code=503, detail="Crawler internal token is not configured")
    if not secrets.compare_digest(x_crawler_token, settings.internal_token):
        raise HTTPException(status_code=401, detail="Invalid crawler token")
    result = await use_case.execute([payload.record.model_dump(mode="json")])
    return StandardResponse(
        success=True,
        message=f"Indexed {result.total_indexed} crawled video.",
        data=IngestionResponseData(
            total_processed=result.total_processed,
            total_indexed=result.total_indexed,
            extracted_hooks=result.extracted_hooks,
            indexed_ids=result.indexed_ids,
        ),
    )
