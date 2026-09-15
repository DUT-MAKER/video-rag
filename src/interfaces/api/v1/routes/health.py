"""Health check route."""

from typing import Any

from fastapi import APIRouter, Depends

from src.core.ports.vector_store_port import IVectorStorePort
from src.interfaces.api.dependencies import get_vector_store_adapter
from src.interfaces.schemas.response_dtos import StandardResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=StandardResponse[dict[str, Any]])
async def health_check(
    vector_store: IVectorStorePort = Depends(get_vector_store_adapter),
) -> StandardResponse[dict[str, Any]]:
    """Check system health status and total count of indexed patterns."""
    total_indexed = await vector_store.count()
    return StandardResponse(
        success=True,
        message="RAG Viral Video service is healthy and operational.",
        data={
            "status": "healthy",
            "total_indexed_patterns": total_indexed,
            "version": "0.1.0",
        },
    )
