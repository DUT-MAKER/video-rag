"""Dishka dependency injection setup for FastAPI."""

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from backend.di.providers import (
    ClientProvider,
    DatabaseProvider,
    RepositoryProvider,
    UseCaseProvider,
    VideoRagProvider,
)


def setup_di(app: FastAPI):
    """Sets up Dishka dependency injection container and binds it to the FastAPI app."""
    container = make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        ClientProvider(),
        VideoRagProvider(),
        UseCaseProvider(),
    )

    app.state.dishka_container = container
    setup_dishka(container, app)
