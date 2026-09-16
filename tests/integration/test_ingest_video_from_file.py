"""Integration test for full end-to-end video extraction and ingestion pipeline."""

import asyncio
import os
import shutil
import tempfile
import pytest

from module.video_rag.infra.data_readers.json_reader_adapter import (
    JsonDataReaderAdapter,
)
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
from module.video_rag.infra.vector_store.chroma_adapter import (
    ChromaVectorStoreAdapter,
)
from module.video_rag.service.video_extraction_service import (
    VideoExtractionPipelineService,
)
from module.video_rag.use_case.ingest_video_data import IngestVideoDataUseCase
from module.video_rag.use_case.search_viral_patterns import (
    SearchViralPatternsUseCase,
)


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
        "-f", "lavfi", "-i", "testsrc=duration=3:size=320x240:rate=25",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=3",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
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
    chroma_dir = os.path.join(temp_workspace, "chroma")
    vector_store = ChromaVectorStoreAdapter(
        persist_dir=chroma_dir,
        collection_name="test_video_pipeline_coll",
    )
    embedding_port = SelfHostedEmbeddingAdapter(fallback_mode=True)
    llm_port = SelfHostedLLMAdapter(fallback_mode=True)
    media_extractor = FFmpegMediaExtractorAdapter()
    thumbnail_selector = VisionThumbnailSelectorAdapter(fallback_mode=True)
    transcriber = BentoWhisperXAdapter(fallback_mode=True)
    data_reader = JsonDataReaderAdapter()

    extract_service = VideoExtractionPipelineService(
        media_extractor_port=media_extractor,
        transcriber_port=transcriber,
        thumbnail_selector_port=thumbnail_selector,
        llm_port=llm_port,
    )

    # 2. Wire single unified use case
    ingest_use_case = IngestVideoDataUseCase(
        embedding_port=embedding_port,
        vector_store_port=vector_store,
        extract_service=extract_service,
        data_reader=data_reader,
    )

    # 3. Execute pipeline via dict input
    payload = {
        "video_path": synthetic_video,
        "language": "vi",
        "enable_diarization": True,
    }
    result = await ingest_use_case.execute(payload)

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
    assert os.path.exists(extraction.thumbnail_path)

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
