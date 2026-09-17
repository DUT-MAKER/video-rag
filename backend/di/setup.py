"""Dishka dependency injection setup for FastAPI."""

from fastapi import FastAPI

from backend.di.dependency_health import validate_runtime_dependencies


def setup_di(app: FastAPI):
    """Sets up Dishka dependency injection container and binds it to the FastAPI app."""
    validate_runtime_dependencies()

    # Import only after the preflight check. Dishka inspects optional package
    # versions during import and otherwise exposes a cryptic regex TypeError.
    from dishka import make_async_container
    from dishka.integrations.fastapi import setup_dishka

    from backend.di.providers import (
        AuthModuleProvider,
        DatabaseSessionProvider,
        UploadModuleProvider,
        VideoRagModuleProvider,
    )
    from video_crawler.di import CrawlerModuleProvider

    container = make_async_container(
        DatabaseSessionProvider(),
        AuthModuleProvider(),
        UploadModuleProvider(),
        VideoRagModuleProvider(),
        CrawlerModuleProvider(),
    )

    app.state.dishka_container = container
    setup_dishka(container, app)
