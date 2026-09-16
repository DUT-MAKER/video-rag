"""Concrete implementation of IS3Client for S3-compatible storage (AWS S3, MinIO)."""

from typing import Any

import boto3
from botocore.config import Config

from core.config import s3_settings
from module.upload.port.s3_client import IS3Client


class S3Client(IS3Client):
    """Boto3 implementation of S3Client interface for AWS S3 and MinIO."""

    def __init__(self) -> None:
        scheme = "https" if s3_settings.secure else "http"
        endpoint_url = None
        if s3_settings.endpoint:
            endpoint_url = f"{scheme}://{s3_settings.endpoint}"

        self._endpoint_url = endpoint_url
        self._client = boto3.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=s3_settings.access_key,
            aws_secret_access_key=s3_settings.secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    def upload_fileobj(self, file_obj: Any, bucket: str, key: str) -> None:
        """Uploads a file-like object synchronously using boto3."""
        self._client.upload_fileobj(file_obj, bucket, key)

    def upload_bytes(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> None:
        """Upload raw bytes to S3/MinIO using boto3."""
        import io

        extra_args = {"ContentType": content_type} if content_type else {}
        self._client.upload_fileobj(
            io.BytesIO(data),
            bucket,
            key,
            ExtraArgs=extra_args if extra_args else None,
        )


    def get_object_url(self, bucket: str, key: str) -> str:
        """Generates the direct HTTP/HTTPS URL for the S3 object."""
        if self._endpoint_url:
            return f"{self._endpoint_url}/{bucket}/{key}"
        return f"https://{bucket}.s3.amazonaws.com/{key}"

    def generate_presigned_upload_url(
        self, bucket: str, key: str, content_type: str, expires_in: int = 3600
    ) -> str:
        """Generates a presigned PUT upload URL using boto3."""
        return self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )
