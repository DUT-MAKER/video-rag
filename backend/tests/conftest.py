import asyncio
from collections.abc import AsyncIterable, Generator

import pytest
import pytest_asyncio
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import module.auth.infra.persistence.models.user  # noqa: F401
from backend.di.providers import AuthModuleProvider
from module.auth.infra.persistence.models.base import Base
from module.upload.port.s3_client import IS3Client
from module.upload.use_case.presign_upload import PresignUploadUseCase
from module.upload.use_case.upload_file import UploadFileUseCase

# SQLite In-memory Database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class TestDatabaseProvider(Provider):
    def __init__(self, session_maker) -> None:
        super().__init__()
        self.session_maker = session_maker

    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncIterable[AsyncSession]:
        async with self.session_maker() as session:
            yield session
            await session.commit()


class TestClientProvider(Provider):
    scope = Scope.APP

    @provide
    def get_s3_client(self) -> IS3Client:
        class MockS3Client:
            def ensure_bucket_exists(self, bucket: str) -> None:
                pass

            def upload_fileobj(self, file_obj, bucket, key):
                pass

            def upload_bytes(self, bucket, key, data, content_type="application/octet-stream"):
                pass

            def upload_file(self, file_path, bucket, key, content_type=None):
                return f"http://mock-s3/{bucket}/{key}"

            def get_object_url(self, bucket, key):
                return f"http://mock-s3/{bucket}/{key}"

            def generate_presigned_upload_url(self, bucket, key, content_type, expires_in=3600):
                return f"http://mock-s3/{bucket}/{key}?presigned=true"

        return MockS3Client()


class TestUploadModuleProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def upload_file_use_case(self, s3_client: IS3Client) -> UploadFileUseCase:
        return UploadFileUseCase(s3_client=s3_client)

    @provide
    def presign_upload_use_case(self, s3_client: IS3Client) -> PresignUploadUseCase:
        return PresignUploadUseCase(s3_client=s3_client)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session_maker(test_engine):
    session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    yield session_maker
    # Reset DB between tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function")
async def test_app(test_session_maker) -> AsyncIterable[FastAPI]:
    from fastapi import FastAPI

    from backend.presentation.api.exceptions import setup_exception_handlers
    from backend.presentation.api.v1.auth import router as auth_router
    from backend.presentation.api.v1.me import router as me_router
    from backend.presentation.api.v1.uploads import router as uploads_router

    app = FastAPI(title="Test App")
    setup_exception_handlers(app)

    container = make_async_container(
        TestDatabaseProvider(test_session_maker),
        AuthModuleProvider(),
        TestClientProvider(),
        TestUploadModuleProvider(),
    )
    setup_dishka(container, app)

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(me_router, prefix="/api/v1")
    app.include_router(uploads_router, prefix="/api/v1")

    yield app
    await container.close()


@pytest_asyncio.fixture(scope="function")
async def client(test_app) -> AsyncIterable[AsyncClient]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
