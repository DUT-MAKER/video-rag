"""Upload file directly use case."""

import uuid
from pathlib import Path
from fastapi import UploadFile

from core.config import s3_settings
from core.exceptions import BadRequestException
from module.upload.domain.entities.uploaded_file import UploadedFileResult
from module.upload.port.s3_client import IS3Client


class UploadFileUseCase:
    """Use case to upload a file to S3/MinIO storage."""

    def __init__(self, s3_client: IS3Client) -> None:
        self._s3_client = s3_client

    async def execute(self, file: UploadFile, prefix: str = "general") -> UploadedFileResult:
        if not file.filename:
            raise BadRequestException("File name is missing")

        if (
            not s3_settings.access_key
            or not s3_settings.secret_key
            or not s3_settings.endpoint
        ):
            # Development fallback when S3 credentials are not set
            return UploadedFileResult(
                filename=file.filename,
                url=f"http://localhost:8000/static/uploads/{file.filename}",
                size_bytes=0,
                content_type=file.content_type or "application/octet-stream",
            )

        content = await file.read()
        file_ext = Path(file.filename).suffix
        unique_name = f"{uuid.uuid4().hex}{file_ext}"
        key = f"{prefix}/{unique_name}"

        self._s3_client.upload_bytes(
            bucket=s3_settings.bucket_name,
            key=key,
            data=content,
            content_type=file.content_type or "application/octet-stream",
        )
        public_url = self._s3_client.get_object_url(s3_settings.bucket_name, key)

        return UploadedFileResult(
            filename=file.filename,
            url=public_url,
            size_bytes=len(content),
            content_type=file.content_type or "application/octet-stream",
        )
