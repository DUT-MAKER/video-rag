import asyncio
import os

import httpx
import pytest


@pytest.mark.network
@pytest.mark.asyncio
async def test_one_complete_video_per_platform() -> None:
    if os.getenv("VIDEO_CRAWLER_RUN_NETWORK") != "1":
        pytest.skip("Set VIDEO_CRAWLER_RUN_NETWORK=1 for the bounded live acceptance test")
    base_url = os.environ["CRAWLER_ACCEPTANCE_API_URL"].rstrip("/")
    token = os.environ["CRAWLER_ACCEPTANCE_ADMIN_TOKEN"]
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=30) as client:
        response = await client.post(
            "/api/v1/crawler/jobs",
            json={
                "platforms": ["facebook", "tiktok", "youtube"],
                "discovery_method": "keyword",
                "query": os.getenv("CRAWLER_ACCEPTANCE_QUERY", "short video"),
                "max_items_per_platform": 1,
            },
        )
        response.raise_for_status()
        job_id = response.json()["job_id"]
        for _ in range(120):
            job = (await client.get(f"/api/v1/crawler/jobs/{job_id}")).json()
            if job["status"] in {"completed", "partial", "failed"}:
                break
            await asyncio.sleep(2)
        videos = (await client.get("/api/v1/crawler/videos", params={"limit": 10})).json()
    matching = [item for item in videos if str(item["job_id"]) == job_id]
    assert {item["platform"] for item in matching} == {"facebook", "tiktok", "youtube"}
    for item in matching:
        assert all(item[field] for field in ("caption", "hashtag", "image_url", "video_url"))
