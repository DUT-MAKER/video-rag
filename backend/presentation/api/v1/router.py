"""API v1 master router."""

from fastapi import APIRouter

from backend.presentation.api.v1.auth import router as auth_router
from backend.presentation.api.v1.chat import router as chat_router
from backend.presentation.api.v1.health import router as health_router
from backend.presentation.api.v1.me import router as me_router
from backend.presentation.api.v1.uploads import router as uploads_router
from backend.presentation.api.v1.video_rag import router as video_rag_router

api_v1_router = APIRouter(prefix="/api/v1")

# Mount sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(me_router)
api_v1_router.include_router(uploads_router)
api_v1_router.include_router(video_rag_router)
api_v1_router.include_router(chat_router)
