"""Integration test for full end-to-end video extraction and ingestion pipeline."""

import asyncio
import os
import shutil
import tempfile

import pytest

from module.video_rag.domain.entities.reference_pattern import SimilarVideoContext
from module.video_rag.infra.embeddings.self_hosted_embed import (
    SelfHostedEmbeddingAdapter,
)
from module.video_rag.infra.llm.self_hosted_llm import SelfHostedLLMAdapter
from module.video_rag.infra.media_extractor.ffmpeg_adapter import (
    FFmpegMediaExtractorAdapter,
)
from module.video_rag.infra.thumbnail_selector.vision_adapter import (
    VisionThumbnailSelectorAdapter,
)
from module.video_rag.infra.transcriber.bento_whisperx_adapter import (
    BentoWhisperXAdapter,
)
from module.video_rag.port.vector_store_port import IVectorStorePort
from module.video_rag.service.video_extraction_service import (
    VideoExtractionPipelineService,
)
from module.video_rag.use_case.ingest_video_data import (
    IngestVideoDataUseCase,
    VideoItemInput,
)
from module.video_rag.use_case.search_viral_patterns import (
    SearchViralPatternsUseCase,
)

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is required for synthetic video test")


class FakeVectorStorePort(IVectorStorePort):
    def __init__(self) -> None:
        self.storage: list[dict] = []

    async def upsert(self, id: str, vector: list[float], metadata: dict, document: str) -> None:
        self.storage.append({"id": id, "vector": vector, "metadata": metadata, "document": document})

    async def upsert_batch(
        self, ids: list[str], vectors: list[list[float]], metadatas: list[dict], documents: list[str]
    ) -> None:
        for i in range(len(ids)):
            self.storage.append(
                {
                    "id": ids[i],
                    "vector": vectors[i],
                    "metadata": metadatas[i],
                    "document": documents[i],
                }
            )

    async def search(self, query_vector: list[float], top_k: int = 5) -> list[SimilarVideoContext]:
        results = []
        for item in self.storage[:top_k]:
            results.append(
                SimilarVideoContext(
                    id=item["id"],
                    document=item["document"],
                    metadata=item["metadata"],
                    score=0.95,
                )
            )
        return results

    async def count(self) -> int:
        return len(self.storage)


@pytest.fixture
def temp_workspace():
    d = tempfile.mkdtemp(prefix="test_pipeline_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
async def synthetic_video(temp_workspace):
    """Generate a short 3-second test video with audio using ffmpeg."""
    video_path = os.path.join(temp_workspace, "test_viral_video.mp4")
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "testsrc=duration=3:size=320x240:rate=25",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=1000:duration=3",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        video_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    assert os.path.exists(video_path)
    return video_path


async def test_end_to_end_video_ingest_pipeline(temp_workspace, synthetic_video):
    # 1. Wire adapters with fallback mode for test environment
    vector_store = FakeVectorStorePort()
    embedding_port = SelfHostedEmbeddingAdapter(fallback_mode=True)
    llm_port = SelfHostedLLMAdapter(fallback_mode=True)
    media_extractor = FFmpegMediaExtractorAdapter()
    thumbnail_selector = VisionThumbnailSelectorAdapter(fallback_mode=True)
    transcriber = BentoWhisperXAdapter(fallback_mode=True)

    from module.video_rag.service.video_store_service import VideoStoreService

    class MockTestS3Client:
        def upload_file(self, file_path, bucket, key, content_type=None):
            return f"https://dutmakers3.dutai.io.vn/{bucket}/{key}"

        def upload_bytes(self, bucket, key, data, content_type="application/octet-stream"):
            return f"https://dutmakers3.dutai.io.vn/{bucket}/{key}"

        def ensure_bucket_exists(self, bucket: str) -> None:
            pass

    video_store_service = VideoStoreService(s3_client=MockTestS3Client())

    extract_service = VideoExtractionPipelineService(
        media_extractor_port=media_extractor,
        transcriber_port=transcriber,
        thumbnail_selector_port=thumbnail_selector,
        llm_port=llm_port,
        video_store_service=video_store_service,
    )

    # 2. Wire single unified use case
    ingest_use_case = IngestVideoDataUseCase(
        embedding_port=embedding_port,
        vector_store_port=vector_store,
        extract_service=extract_service,
    )

    # 3. Execute pipeline via VideoItemInput
    input_data = VideoItemInput(
        video_path=synthetic_video,
        language="vi",
    )
    result = await ingest_use_case.execute(input_data=input_data)

    # 4. Assert extraction and ingestion output
    assert result.total_indexed == 1
    assert result.total_processed == 1

    extraction = result.latest_extraction
    record = result.latest_record
    assert extraction is not None
    assert record is not None

    assert extraction.speaker_count >= 1
    assert len(record.caption) > 0
    assert len(record.summary) > 0
    assert "#" in record.hashtag
    assert "https://dutmakers3.dutai.io.vn" in extraction.thumbnail_path

    # 5. Verify vector store state
    assert len(vector_store.storage) == 1
    stored = vector_store.storage[0]
    assert stored["metadata"]["caption"] == record.caption
    search_uc = SearchViralPatternsUseCase(
        embedding_port=embedding_port,
        vector_store_port=vector_store,
    )
    search_results = await search_uc.execute(query="quy tắc 2 phút thói quen", top_k=1)
    assert len(search_results) == 1
    assert search_results[0].caption == record.caption
