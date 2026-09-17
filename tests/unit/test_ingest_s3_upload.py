"""Unit tests for S3/MinIO upload integration in IngestVideoDataUseCase."""

import os
import tempfile
from unittest.mock import MagicMock

import pytest

from module.upload.port.s3_client import IS3Client
from module.video_rag.domain.entities.extraction_result import (
    TranscriptSegment,
    VideoExtractionResult,
)
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.vector_store_port import IVectorStorePort
from module.video_rag.service.video_extraction_service import (
    VideoExtractionPipelineService,
)
from module.video_rag.use_case.ingest_video_data import (
    IngestVideoDataUseCase,
    VideoItemInput,
)


class MockEmbeddingPort(IEmbeddingPort):
    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class MockVectorStorePort(IVectorStorePort):
    def __init__(self) -> None:
        self.upserted_records: list[dict] = []

    async def upsert(
        self,
        id: str,
        vector: list[float],
        metadata: dict,
        document: str,
    ) -> None:
        self.upserted_records.append({"id": id, "vector": vector, "metadata": metadata, "document": document})

    async def upsert_batch(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
        documents: list[str],
    ) -> None:
        for i, doc_id in enumerate(ids):
            self.upserted_records.append(
                {"id": doc_id, "vector": vectors[i], "metadata": metadatas[i], "document": documents[i]}
            )

    async def query_similar(self, query_vector: list[float], top_k: int = 5) -> list:
        return []

    async def count(self) -> int:
        return len(self.upserted_records)


@pytest.fixture
def dummy_video_and_thumb():
    video_fd, video_path = tempfile.mkstemp(suffix=".mp4")
    os.write(video_fd, b"dummy_mp4_bytes")
    os.close(video_fd)

    thumb_fd, thumb_path = tempfile.mkstemp(suffix=".jpg")
    os.write(thumb_fd, b"dummy_jpg_bytes")
    os.close(thumb_fd)

    yield video_path, thumb_path

    for p in (video_path, thumb_path):
        if os.path.exists(p):
            os.unlink(p)


@pytest.mark.asyncio
async def test_ingest_uploads_video_and_thumbnail_to_s3(dummy_video_and_thumb):
    video_path, thumb_path = dummy_video_and_thumb

    # Mock extract service
    mock_extract = MagicMock(spec=VideoExtractionPipelineService)
    mock_extract.execute.return_value = VideoExtractionResult(
        video_path=video_path,
        transcript="Bí quyết tăng trưởng video viral trong 30 giây đầu tiên.",
        transcript_with_speakers="SPEAKER_00 [0.0s -> 4.0s]: Bí quyết tăng trưởng video viral trong 30 giây đầu tiên.",
        thumbnail_path=thumb_path,
        caption="Cách làm video viral",
        hashtag="#viral #growth",
        summary="Tóm tắt nội dung video viral",
        transcript_segments=[
            TranscriptSegment(start=0.0, end=4.0, text="Bí quyết tăng trưởng", speaker="SPEAKER_00")
        ],
        speaker_count=1,
        duration_seconds=30.0,
    )

    # Mock S3 client
    mock_s3 = MagicMock(spec=IS3Client)
    mock_s3.get_object_url.side_effect = (
        lambda bucket, key: f"https://dutmakers3.dutai.io.vn/{bucket}/{key}"
    )

    embed_port = MockEmbeddingPort()
    vector_store = MockVectorStorePort()

    use_case = IngestVideoDataUseCase(
        embedding_port=embed_port,
        vector_store_port=vector_store,
        extract_service=mock_extract,
        s3_client=mock_s3,
    )

    result = await use_case.execute(
        VideoItemInput(
            video_path=video_path,
            caption="Cách làm video viral",
            hashtag="#viral",
            language="vi",
        )
    )

    # Assert S3 upload_file called for both video and thumbnail
    assert mock_s3.upload_file.call_count == 2
    video_upload_call = mock_s3.upload_file.call_args_list[0]
    thumb_upload_call = mock_s3.upload_file.call_args_list[1]

    assert video_upload_call.kwargs["file_path"] == video_path
    assert "videos/" in video_upload_call.kwargs["key"]
    assert video_upload_call.kwargs["content_type"] == "video/mp4"

    assert thumb_upload_call.kwargs["file_path"] == thumb_path
    assert "thumbnails/" in thumb_upload_call.kwargs["key"]
    assert thumb_upload_call.kwargs["content_type"] == "image/jpeg"

    # Assert record and vector store have S3 URLs
    record = result.latest_record
    assert record is not None
    assert record.video_url.startswith("https://dutmakers3.dutai.io.vn/video-rag/videos/")
    assert record.image_url.startswith("https://dutmakers3.dutai.io.vn/video-rag/thumbnails/")

    # Assert metadata in vector store has the MinIO S3 URLs
    assert len(vector_store.upserted_records) == 1
    stored_meta = vector_store.upserted_records[0]["metadata"]
    assert stored_meta["video_url"] == record.video_url
    assert stored_meta["image_url"] == record.image_url


@pytest.mark.asyncio
async def test_ingest_fallback_when_s3_fails(dummy_video_and_thumb):
    video_path, thumb_path = dummy_video_and_thumb

    mock_extract = MagicMock(spec=VideoExtractionPipelineService)
    mock_extract.execute.return_value = VideoExtractionResult(
        video_path=video_path,
        transcript="Test transcript",
        transcript_with_speakers="SPEAKER_00: Test transcript",
        thumbnail_path=thumb_path,
        caption="Test caption",
        summary="Test summary",
    )

    # Mock S3 client that raises error
    mock_s3 = MagicMock(spec=IS3Client)
    mock_s3.upload_file.side_effect = RuntimeError("S3 Connection timeout")

    use_case = IngestVideoDataUseCase(
        embedding_port=MockEmbeddingPort(),
        vector_store_port=MockVectorStorePort(),
        extract_service=mock_extract,
        s3_client=mock_s3,
    )

    # Ingestion should NOT crash; it falls back to local paths
    result = await use_case.execute(
        VideoItemInput(video_path=video_path, caption="Test", language="vi")
    )

    record = result.latest_record
    assert record is not None
    assert record.video_url == video_path
    assert record.image_url == thumb_path
