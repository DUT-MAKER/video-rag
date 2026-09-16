"""Store accepted crawler artifacts in the project's S3/MinIO bucket."""

from __future__ import annotations

import asyncio
import mimetypes
from pathlib import Path

import boto3
from botocore.config import Config

from core.config import S3Settings
from video_crawler.config import CrawlerSettings
from video_crawler.domain import DiscoveredVideo, MediaArtifact


class S3CrawlerStorage:
    def __init__(self, s3: S3Settings, crawler: CrawlerSettings) -> None:
        scheme = "https" if s3.secure else "http"
        self.endpoint = f"{scheme}://{s3.endpoint}" if s3.endpoint else ""
        self.bucket = s3.bucket_name
        self.prefix = crawler.minio_prefix.strip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint or None,
            aws_access_key_id=s3.access_key,
            aws_secret_access_key=s3.secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    async def store(self, video: DiscoveredVideo, artifact: MediaArtifact) -> tuple[str, str]:
        base = f"{self.prefix}/{video.platform.value}/{video.platform_video_id}"
        video_path = Path(artifact.video_path)
        image_path = Path(artifact.thumbnail_path) if artifact.thumbnail_path else None
        if image_path is None or not image_path.exists():
            raise RuntimeError("THUMBNAIL_MISSING: no thumbnail was produced")
        video_key = f"{base}/original{video_path.suffix.lower() or '.mp4'}"
        image_key = f"{base}/thumbnail{image_path.suffix.lower() or '.jpg'}"
        await asyncio.to_thread(self._upload, video_path, video_key)
        await asyncio.to_thread(self._upload, image_path, image_key)
        return self._url(video_key), self._url(image_key)

    def _upload(self, path: Path, key: str) -> None:
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.client.upload_file(str(path), self.bucket, key, ExtraArgs={"ContentType": content_type})

    def _url(self, key: str) -> str:
        if self.endpoint:
            return f"{self.endpoint}/{self.bucket}/{key}"
        return f"https://{self.bucket}.s3.amazonaws.com/{key}"
