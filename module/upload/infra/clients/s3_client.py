"""Concrete implementation of IS3Client for S3-compatible storage (AWS S3, MinIO)."""

import json
import mimetypes
import os
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from loguru import logger

from core.config import s3_settings
from module.upload.port.s3_client import IS3Client


class S3Client(IS3Client):
    """Boto3 implementation of S3Client interface for AWS S3 and MinIO."""

    def __init__(self) -> None:
        scheme = "https" if s3_settings.secure else "http"
        clean_endpoint = s3_settings.clean_endpoint
        self.endpoint_url = f"{scheme}://{clean_endpoint}"

        self._client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=s3_settings.access_key,
            aws_secret_access_key=s3_settings.secret_key,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
            region_name="us-east-1",
        )

    def set_bucket_public(self, bucket: str) -> None:
        """Applies a public-read bucket policy so that uploaded objects can be accessed anonymously."""
        public_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                }
            ],
        }
        try:
            self._client.put_bucket_policy(
                Bucket=bucket,
                Policy=json.dumps(public_policy),
            )
            logger.info(f"🔓 Đã cấu hình policy PUBLIC READ cho bucket '{bucket}'.")
        except Exception as err:
            logger.warning(f"⚠️ Không thể set public policy cho bucket {bucket}: {err}")

    def ensure_bucket_exists(self, bucket: str) -> None:
        """Checks if bucket exists; if not, creates it and sets public read policy."""
        try:
            self._client.head_bucket(Bucket=bucket)
            self.set_bucket_public(bucket)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in ("404", "NoSuchBucket"):
                logger.info(f"🪣 Bucket '{bucket}' không tồn tại. Đang tạo mới trên MinIO...")
                self._client.create_bucket(Bucket=bucket)
                logger.info(f"✅ Đã tạo bucket '{bucket}' thành công.")
                self.set_bucket_public(bucket)
            else:
                try:
                    self._client.create_bucket(Bucket=bucket)
                    self.set_bucket_public(bucket)
                except Exception as create_err:
                    logger.warning(f"Could not create bucket {bucket}: {create_err}")

    def upload_fileobj(self, file_obj: Any, bucket: str, key: str) -> None:
        """Uploads a file-like object synchronously using boto3."""
        self.ensure_bucket_exists(bucket)
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

        self.ensure_bucket_exists(bucket)
        extra_args = {"ContentType": content_type} if content_type else {}
        self._client.upload_fileobj(
            io.BytesIO(data),
            bucket,
            key,
            ExtraArgs=extra_args if extra_args else None,
        )

    def upload_file(
        self,
        file_path: str,
        bucket: str,
        key: str,
        content_type: str | None = None,
    ) -> str:
        """Uploads a local file from disk directly to S3/MinIO and returns public URL."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file does not exist: {file_path}")

        self.ensure_bucket_exists(bucket)

        if not content_type:
            guessed_type, _ = mimetypes.guess_type(file_path)
            content_type = guessed_type or "application/octet-stream"

        extra_args = {"ContentType": content_type}
        self._client.upload_file(
            file_path,
            bucket,
            key,
            ExtraArgs=extra_args,
        )
        return self.get_object_url(bucket, key)

    def get_object_url(self, bucket: str, key: str) -> str:
        """Generates the direct HTTP/HTTPS URL for the S3 object."""
        return f"{self.endpoint_url}/{bucket}/{key}"

    def generate_presigned_upload_url(self, bucket: str, key: str, content_type: str, expires_in: int = 3600) -> str:
        """Generates a presigned PUT upload URL using boto3."""
        self.ensure_bucket_exists(bucket)
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

