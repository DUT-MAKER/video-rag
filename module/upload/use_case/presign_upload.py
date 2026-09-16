"""Presign upload use case."""

import uuid
from pathlib import Path

from pydantic import BaseModel

from core.config import s3_settings
from core.exceptions import BadRequestException
from module.upload.port.s3_client import IS3Client


class PresignUploadOutputDTO(BaseModel):
    """Output DTO for presigned upload URL."""

    upload_url: str
    object_key: str
    public_url: str
    expires_in_seconds: int = 3600

    @property
    def presigned_url(self) -> str:
        return self.upload_url

    @property
    def key(self) -> str:
        return self.object_key


class PresignUploadUseCase:
    """Use case to generate a presigned S3 upload URL."""

    def __init__(self, s3_client: IS3Client) -> None:
        self._s3_client = s3_client

    async def execute(
        self,
        filename: str | None = None,
        key: str | None = None,
        content_type: str = "application/octet-stream",
        prefix: str = "uploads",
    ) -> PresignUploadOutputDTO:
        if not filename and not key:
            raise BadRequestException("Filename or key is required")

        if key:
            safe_key = key
        else:
            file_ext = Path(filename).suffix if filename else ""
            safe_key = f"{prefix}/{uuid.uuid4().hex}{file_ext}"

        upload_url = self._s3_client.generate_presigned_upload_url(
            bucket=s3_settings.bucket_name,
            key=safe_key,
            content_type=content_type,
            expires_in=3600,
        )
        public_url = self._s3_client.get_object_url(s3_settings.bucket_name, safe_key)

        return PresignUploadOutputDTO(
            upload_url=upload_url,
            object_key=safe_key,
            public_url=public_url,
            expires_in_seconds=3600,
        )
