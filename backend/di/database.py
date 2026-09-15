"""Database engine and session factory configuration for Dishka."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import app_settings, db_settings

async_engine = create_async_engine(
    db_settings.url,
    echo=app_settings.debug,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
