"""Health check router."""

from fastapi import APIRouter
from core.config import app_settings, vector_store_settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Service health status")
async def health_check():
    """Service health check."""
    return {
        "status": "ok",
        "app_name": app_settings.name,
        "environment": app_settings.env,
        "vector_store": vector_store_settings.store_type,
    }

