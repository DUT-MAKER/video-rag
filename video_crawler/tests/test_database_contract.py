import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.integration
@pytest.mark.asyncio
async def test_migrated_crawler_schema_contract() -> None:
    database_url = os.getenv("CRAWLER_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("CRAWLER_TEST_DATABASE_URL is not configured")
    engine = create_async_engine(database_url)
    async with engine.connect() as connection:
        rows = await connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'video_crawler' ORDER BY table_name"
            )
        )
        assert [row[0] for row in rows] == ["crawl_jobs", "videos"]
    await engine.dispose()
