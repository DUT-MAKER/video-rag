"""Upload file directly use case."""

import uuid
from pathlib import Path

from core.config import s3_settings
from core.exceptions import BadRequestException
from module.upload.domain.entities.uploaded_file import UploadedFileResult
from module.upload.port.s3_client import IS3Client


class UploadFileUseCase:
    """Use case to upload a file to S3/MinIO storage."""

    def __init__(self, s3_client: IS3Client) -> None:
        self._s3_client = s3_client

    async def execute(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
        prefix: str = "uploads",
    ) -> UploadedFileResult:
        if not filename:
            raise BadRequestException("File name is missing")

        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{file_ext}"
        key = f"{prefix}/{unique_name}"

        self._s3_client.upload_bytes(
            bucket=s3_settings.bucket_name,
            key=key,
            data=file_content,
            content_type=content_type,
        )
        public_url = self._s3_client.get_object_url(s3_settings.bucket_name, key)

        return UploadedFileResult(
            key=key,
            public_url=public_url,
            filename=filename,
            size_bytes=len(file_content),
            content_type=content_type,
        )
