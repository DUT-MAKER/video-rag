"""Health check router."""

from typing import Any

from fastapi import APIRouter

from backend.presentation.schemas.response_dtos import StandardResponse
from core.config import app_settings, vector_store_settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=StandardResponse[dict[str, Any]], summary="Service health status")
async def health_check() -> StandardResponse[dict[str, Any]]:
    """Service health check."""
    return StandardResponse(
        success=True,
        message="Service is healthy",
        data={
            "status": "healthy",
            "app_name": app_settings.name,
            "environment": app_settings.env,
            "vector_store": vector_store_settings.store_type,
            "total_indexed_patterns": 0,
        },
    )


