"""Unit tests for VideoStoreService.

Verifies async upload methods for videos and thumbnails to MinIO/S3.
"""

import tempfile
from pathlib import Path

import pytest

from module.video_rag.service.video_store_service import VideoStoreService


class MockS3ClientForTest:
    def __init__(self):
        self.uploaded_files = []
        self.uploaded_bytes = []
        self.buckets_checked = []

    def ensure_bucket_exists(self, bucket: str) -> None:
        self.buckets_checked.append(bucket)

    def upload_file(self, file_path, bucket, key, content_type=None):
        self.uploaded_files.append((file_path, bucket, key, content_type))
        return f"https://dutmakers3.dutai.io.vn/{bucket}/{key}"

    def upload_bytes(self, bucket, key, data, content_type="application/octet-stream"):
        self.uploaded_bytes.append((bucket, key, len(data), content_type))
        return f"https://dutmakers3.dutai.io.vn/{bucket}/{key}"

    def upload_fileobj(self, file_obj, bucket, key):
        pass

    def get_object_url(self, bucket, key):
        return f"https://dutmakers3.dutai.io.vn/{bucket}/{key}"

    def generate_presigned_upload_url(self, bucket, key, content_type, expires_in=3600):
        return f"https://dutmakers3.dutai.io.vn/{bucket}/{key}?presigned=true"


@pytest.fixture
def mock_s3():
    return MockS3ClientForTest()


@pytest.fixture
def video_store(mock_s3):
    return VideoStoreService(s3_client=mock_s3)


@pytest.mark.asyncio
async def test_upload_video_file(video_store: VideoStoreService, mock_s3: MockS3ClientForTest):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(b"\x00\x00\x00\x18ftypmp42")
        temp_video_path = f.name

    try:
        url = await video_store.upload_video_file(
            local_file_path=temp_video_path,
            filename="sample_dance.mp4",
        )
        assert "https://dutmakers3.dutai.io.vn" in url
        assert "videos/" in url
        assert url.endswith(".mp4")
        assert len(mock_s3.uploaded_files) == 1
        assert mock_s3.uploaded_files[0][3] == "video/mp4"
    finally:
        Path(temp_video_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_upload_video_bytes(video_store: VideoStoreService, mock_s3: MockS3ClientForTest):
    data = b"synthetic video raw bytes"
    url = await video_store.upload_video_bytes(
        data=data,
        filename="test_clip.mp4",
        content_type="video/mp4",
    )
    assert "https://dutmakers3.dutai.io.vn" in url
    assert "videos/" in url
    assert len(mock_s3.uploaded_bytes) == 1
    assert mock_s3.uploaded_bytes[0][2] == len(data)


@pytest.mark.asyncio
async def test_upload_thumbnail_file(video_store: VideoStoreService, mock_s3: MockS3ClientForTest):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"\xff\xd8\xff\xe0")
        temp_img_path = f.name

    try:
        url = await video_store.upload_thumbnail_file(
            local_image_path=temp_img_path,
            stem="video_12345",
        )
        assert "https://dutmakers3.dutai.io.vn" in url
        assert "thumbnails/video_12345" in url
        assert url.endswith(".jpg")
        assert len(mock_s3.uploaded_files) == 1
    finally:
        Path(temp_img_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_upload_thumbnail_bytes(video_store: VideoStoreService, mock_s3: MockS3ClientForTest):
    img_data = b"\xff\xd8\xff\xe0raw_jpg_data"
    url = await video_store.upload_thumbnail_bytes(
        data=img_data,
        stem="banner_frame",
        content_type="image/jpeg",
    )
    assert "https://dutmakers3.dutai.io.vn" in url
    assert "thumbnails/banner_frame" in url
    assert len(mock_s3.uploaded_bytes) == 1
