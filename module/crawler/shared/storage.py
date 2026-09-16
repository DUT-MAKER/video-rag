"""Storage adapters implementing IStoragePort (shared across all platforms)."""

import os
from pathlib import Path
import shutil

from loguru import logger
from minio import Minio

from core.config import get_s3_settings
from module.crawler.port import IStoragePort


class MinioStorageAdapter(IStoragePort):
    """Production storage adapter uploading assets to S3 / MinIO."""

    def __init__(self):
        settings = get_s3_settings()
        self.endpoint = settings.endpoint
        self.bucket_name = settings.bucket_name
        self.secure = settings.secure

        self.client = Minio(
            self.endpoint,
            access_key=settings.access_key,
            secret_key=settings.secret_key,
            secure=self.secure,
        )
        if not self.client.bucket_exists(self.bucket_name):
            logger.info(f"Creating MinIO bucket: {self.bucket_name}")
            self.client.make_bucket(self.bucket_name)

    def upload_file(self, local_path: str, destination_name: str) -> str:
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found for upload: {local_path}")

        self.client.fput_object(self.bucket_name, destination_name, local_path)
        protocol = "https" if self.secure else "http"
        return f"{protocol}://{self.endpoint}/{self.bucket_name}/{destination_name}"


class LocalStorageAdapter(IStoragePort):
    """Development storage adapter copying assets to a local data directory.
    
    Used when MinIO is not yet running or during local offline testing.
    """

    def __init__(self, base_dir: str = "data/storage"):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStorageAdapter initialized at {self.base_dir}")

    def upload_file(self, local_path: str, destination_name: str) -> str:
        src = Path(local_path).resolve()
        if not src.exists():
            raise FileNotFoundError(f"Local source file not found: {local_path}")

        dest = self.base_dir / destination_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        return str(dest)
