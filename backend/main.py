"""FastAPI application main module configuring routes, middleware, and lifespan."""

from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.di.setup import setup_di
from backend.presentation.api.v1.router import api_v1_router
from core.config import app_settings
from core.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for DI and application resource management."""
    yield
    if hasattr(app.state, "dishka_container"):
        await app.state.dishka_container.close()


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=app_settings.name,
        description=(
            "Clean Architecture & DDD Modular Backend for Viral Video RAG & Copilot.\n\n"
            "### Architecture Overview\n"
            "* **Core Layer (`core/`):** Unified settings, security, JWT, exceptions.\n"
            "* **Module Layer (`module/`):** Feature domains (`auth`, `upload`, `video_rag`).\n"
            "* **Presentation Layer (`backend/`):** FastAPI endpoints, DI container (Dishka), Web UI.\n"
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Setup Dishka Dependency Injection
    setup_di(app)

    # Setup CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global Domain Exception Handler
    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "status_code": exc.status_code,
                }
            },
        )

    # Mount API v1 Routes
    app.include_router(api_v1_router, prefix="/api/v1")

    # Mount Frontend Static UI
    static_path = Path(__file__).resolve().parent / "static"
    if static_path.exists():
        app.mount("/app", StaticFiles(directory=str(static_path), html=True), name="static_ui")

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "message": f"Welcome to {app_settings.name} service.",
            "version": "2.0.0",
            "docs": "/docs",
            "app_name": app_settings.name,
            "environment": app_settings.env,
            "web_ui": "/app/index.html",
        }

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.debug,
    )
