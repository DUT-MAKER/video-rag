"""Dishka providers exposed to the main API process."""

from dishka import Provider, Scope, provide

from backend.di.database import async_session_factory
from video_crawler.config import CrawlerSettings, get_crawler_settings
from video_crawler.infrastructure.repository import CrawlerRepository


class CrawlerModuleProvider(Provider):
    @provide(scope=Scope.APP)
    def crawler_settings(self) -> CrawlerSettings:
        return get_crawler_settings()

    @provide(scope=Scope.APP)
    def crawler_repository(self) -> CrawlerRepository:
        return CrawlerRepository(async_session_factory)
