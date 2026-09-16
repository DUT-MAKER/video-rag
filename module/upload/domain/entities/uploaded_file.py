"""Uploaded file domain entity / value objects."""

from dataclasses import dataclass


@dataclass
class UploadedFileResult:
    key: str
    public_url: str
    presigned_url: str | None = None
    filename: str | None = None
    size_bytes: int = 0
    content_type: str = "application/octet-stream"

