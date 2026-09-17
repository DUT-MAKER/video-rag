"""Storage interface port for S3/MinIO compatible object stores."""

from typing import Any, Protocol


class IS3Client(Protocol):
    """Interface protocol for S3/MinIO storage operations."""

    def upload_fileobj(self, file_obj: Any, bucket: str, key: str) -> None:
        """Upload a file-like object to a specific S3 bucket and key."""
        ...

    def upload_bytes(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> None:
        """Upload raw bytes to a specific S3 bucket and key."""
        ...

    def get_object_url(self, bucket: str, key: str) -> str:
        """Generate and return the public/internal URL for a given bucket and key."""
        ...

    def upload_file(
        self,
        file_path: str,
        bucket: str,
        key: str,
        content_type: str | None = None,
    ) -> None:
        """Upload a local file directly to a specific S3 bucket and key."""
        ...

    def generate_presigned_upload_url(self, bucket: str, key: str, content_type: str, expires_in: int = 3600) -> str:
        """Generate a presigned PUT upload URL."""
        ...
