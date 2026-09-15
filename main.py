"""FastAPI application entrypoint for RAG Viral Video."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.core.domain.exceptions import (
    DomainError,
    DomainValidationError,
    ScriptGenerationError,
    VideoRecordParsingError,
)
from src.infra.config.settings import get_settings
from src.interfaces.api.v1.router import api_v1_router
from src.interfaces.schemas.response_dtos import StandardResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle management."""
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description=(
        "## AI Agent platform for analyzing viral video patterns and generating "
        "short-form video scripts (TikTok, Reels, YouTube Shorts) using RAG.\n\n"
        "### Clean Architecture Highlights:\n"
        "* **Core Layer:** Pure Python (Entities, Value Objects, Ports, Use Cases).\n"
        "* **Infra Layer:** Self-hosted LLM Adapter, Self-hosted Embedding Adapter, "
        "ChromaDB Adapter, JSON Data Reader Adapter.\n"
        "* **Interfaces Layer:** FastAPI REST API, DTOs, Dependency Injection Container."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers for Core Domain Exceptions
@app.exception_handler(DomainValidationError)
async def domain_validation_handler(request: Request, exc: DomainValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "message": str(exc), "data": None},
    )


@app.exception_handler(VideoRecordParsingError)
async def video_parsing_handler(request: Request, exc: VideoRecordParsingError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": str(exc), "data": None},
    )


@app.exception_handler(ScriptGenerationError)
async def script_generation_handler(request: Request, exc: ScriptGenerationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"success": False, "message": str(exc), "data": None},
    )


@app.exception_handler(DomainError)
async def domain_general_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False, "message": f"Domain error: {exc}", "data": None},
    )


# Register API routes
app.include_router(api_v1_router)

# Mount static web assets
static_dir = Path(__file__).resolve().parent / "src" / "interfaces" / "web"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/chat", tags=["Web UI"], response_class=FileResponse)
async def chat_ui() -> FileResponse:
    """Serve ViralCopilot AI Chatbot Web Interface."""
    return FileResponse(str(static_dir / "index.html"))


@app.get("/ui", tags=["Web UI"], include_in_schema=False)
async def ui_redirect() -> RedirectResponse:
    """Convenience redirect to /chat."""
    return RedirectResponse(url="/chat")


@app.get("/", tags=["Root"])
async def root() -> StandardResponse[dict[str, str]]:
    """Root endpoint providing service information and API documentation links."""
    return StandardResponse(
        success=True,
        message="Welcome to RAG Viral Video service.",
        data={
            "app_name": settings.APP_NAME,
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/api/v1/health",
            "chat_ui": "/chat",
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
