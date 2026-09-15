"""API v1 master router."""

from fastapi import APIRouter

from src.interfaces.api.v1.routes.chat import router as chat_router
from src.interfaces.api.v1.routes.generation import router as generation_router
from src.interfaces.api.v1.routes.health import router as health_router
from src.interfaces.api.v1.routes.ingestion import router as ingestion_router
from src.interfaces.api.v1.routes.search import router as search_router

api_v1_router = APIRouter(prefix="/api/v1")

# Mount sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(ingestion_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(generation_router)
api_v1_router.include_router(chat_router)
