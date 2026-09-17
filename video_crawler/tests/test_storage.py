from pathlib import Path

import pytest

from core.config import S3Settings
from video_crawler.config import CrawlerSettings
from video_crawler.domain import DiscoveredVideo, MediaArtifact, Platform
from video_crawler.infrastructure.storage import S3CrawlerStorage


class FakeS3Client:
    def __init__(self) -> None:
        self.uploads: list[tuple[str, str, str, dict[str, str]]] = []

    def upload_file(
        self, path: str, bucket: str, key: str, ExtraArgs: dict[str, str]
    ) -> None:
        self.uploads.append((path, bucket, key, ExtraArgs))


@pytest.mark.asyncio
async def test_storage_uploads_video_and_thumbnail_under_crawler_prefix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = FakeS3Client()
    monkeypatch.setattr("video_crawler.infrastructure.storage.boto3.client", lambda *_, **__: client)
    settings = S3Settings(
        S3_ENDPOINT="localhost:9000",
        S3_ACCESS_KEY="access",
        S3_SECRET_KEY="secret",
        S3_BUCKET_NAME="videos",
        S3_SECURE=False,
    )
    storage = S3CrawlerStorage(settings, CrawlerSettings())
    video_path = tmp_path / "video.mp4"
    thumbnail_path = tmp_path / "thumbnail.jpg"
    video_path.write_bytes(b"video")
    thumbnail_path.write_bytes(b"image")
    discovered = DiscoveredVideo(
        platform=Platform.TIKTOK,
        platform_video_id="123",
        canonical_url="https://www.tiktok.com/@creator/video/123",
        caption="Caption",
    )
    artifact = MediaArtifact(str(video_path), str(thumbnail_path), 5.0, str(tmp_path))

    video_url, image_url = await storage.store(discovered, artifact)

    assert [upload[2] for upload in client.uploads] == [
        "video-crawler/tiktok/123/original.mp4",
        "video-crawler/tiktok/123/thumbnail.jpg",
    ]
    assert video_url == "http://localhost:9000/videos/video-crawler/tiktok/123/original.mp4"
    assert image_url == "http://localhost:9000/videos/video-crawler/tiktok/123/thumbnail.jpg"


def test_storage_rejects_incomplete_configuration() -> None:
    with pytest.raises(RuntimeError, match="S3_CONFIGURATION_INCOMPLETE"):
        S3CrawlerStorage(S3Settings(_env_file=None), CrawlerSettings())
