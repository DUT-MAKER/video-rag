"""VideoStoreService implementation.

Dedicated service for storing video and thumbnail media assets asynchronously
directly to MinIO/S3 object storage without local disk persistence.
"""

import asyncio
import mimetypes
import uuid
from pathlib import Path

from loguru import logger

from core.config import s3_settings
from module.upload.port.s3_client import IS3Client


class VideoStoreService:
    """Service to handle uploading videos, thumbnails, and media assets asynchronously to MinIO S3."""

    def __init__(self, s3_client: IS3Client) -> None:
        self._s3_client = s3_client
        self._bucket = s3_settings.bucket_name

    async def upload_video_bytes(
        self,
        data: bytes,
        filename: str = "video.mp4",
        content_type: str | None = None,
        prefix: str = "videos",
    ) -> str:
        """Upload video bytes asynchronously directly to MinIO and return public URL."""
        if not content_type:
            guessed_type, _ = mimetypes.guess_type(filename)
            content_type = guessed_type or "video/mp4"

        unique_id = uuid.uuid4().hex
        suffix = Path(filename).suffix or ".mp4"
        clean_stem = Path(filename).stem
        s3_key = f"{prefix}/{clean_stem}_{unique_id[:10]}{suffix}"

        logger.info(f"☁️ [VideoStoreService] Async upload video '{filename}' ({len(data)} bytes) -> key='{s3_key}'...")
        await asyncio.to_thread(
            self._s3_client.upload_bytes,
            bucket=self._bucket,
            key=s3_key,
            data=data,
            content_type=content_type,
        )
        url = self._s3_client.get_object_url(self._bucket, s3_key)
        logger.info(f"✅ [VideoStoreService] Upload video thành công: {url}")
        return url

    async def upload_video_file(
        self,
        local_file_path: str,
        filename: str | None = None,
        content_type: str | None = None,
        prefix: str = "videos",
    ) -> str:
        """Upload video from a local temporary path asynchronously to MinIO."""
        fname = filename or Path(local_file_path).name
        if not content_type:
            guessed_type, _ = mimetypes.guess_type(fname)
            content_type = guessed_type or "video/mp4"

        unique_id = uuid.uuid4().hex
        clean_stem = Path(fname).stem
        suffix = Path(fname).suffix or ".mp4"
        s3_key = f"{prefix}/{clean_stem}_{unique_id[:10]}{suffix}"

        logger.info(f"☁️ [VideoStoreService] Async upload video file '{local_file_path}' -> key='{s3_key}'...")
        url = await asyncio.to_thread(
            self._s3_client.upload_file,
            file_path=local_file_path,
            bucket=self._bucket,
            key=s3_key,
            content_type=content_type,
        )
        logger.info(f"✅ [VideoStoreService] Upload video thành công: {url}")
        return url

    async def upload_thumbnail_file(
        self,
        local_image_path: str,
        stem: str = "thumbnail",
        content_type: str = "image/jpeg",
        prefix: str = "thumbnails",
    ) -> str:
        """Upload thumbnail image file asynchronously directly to MinIO and return public URL."""
        unique_id = uuid.uuid4().hex[:8]
        s3_key = f"{prefix}/{stem}_{unique_id}_thumb.jpg"

        logger.info(f"☁️ [VideoStoreService] Async upload thumbnail '{local_image_path}' -> key='{s3_key}'...")
        url = await asyncio.to_thread(
            self._s3_client.upload_file,
            file_path=local_image_path,
            bucket=self._bucket,
            key=s3_key,
            content_type=content_type,
        )
        logger.info(f"✅ [VideoStoreService] Upload thumbnail thành công: {url}")
        return url

    async def upload_thumbnail_bytes(
        self,
        data: bytes,
        stem: str = "thumbnail",
        content_type: str = "image/jpeg",
        prefix: str = "thumbnails",
    ) -> str:
        """Upload raw thumbnail bytes asynchronously directly to MinIO and return public URL."""
        unique_id = uuid.uuid4().hex[:8]
        s3_key = f"{prefix}/{stem}_{unique_id}_thumb.jpg"

        logger.info(f"☁️ [VideoStoreService] Async upload thumbnail bytes ({len(data)} bytes) -> key='{s3_key}'...")
        await asyncio.to_thread(
            self._s3_client.upload_bytes,
            bucket=self._bucket,
            key=s3_key,
            data=data,
            content_type=content_type,
        )
        url = self._s3_client.get_object_url(self._bucket, s3_key)
        logger.info(f"✅ [VideoStoreService] Upload thumbnail bytes thành công: {url}")
        return url
