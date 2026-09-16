"""Dishka dependency injection setup for FastAPI."""

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from backend.di.providers import (
    AuthModuleProvider,
    DatabaseSessionProvider,
    UploadModuleProvider,
    VideoRagModuleProvider,
)


def setup_di(app: FastAPI):
    """Sets up Dishka dependency injection container and binds it to the FastAPI app."""
    container = make_async_container(
        DatabaseSessionProvider(),
        AuthModuleProvider(),
        UploadModuleProvider(),
        VideoRagModuleProvider(),
    )


    app.state.dishka_container = container
    setup_dishka(container, app)
