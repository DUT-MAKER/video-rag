"""Unit tests for ExtractVideoMetadataUseCase with mocked ports."""

import os
import tempfile
from unittest.mock import AsyncMock

import pytest

from module.video_rag.domain.entities.extraction_result import TranscriptSegment
from module.video_rag.port.llm_port import ILLMPort
from module.video_rag.port.media_extractor_port import IMediaExtractorPort
from module.video_rag.port.thumbnail_selector_port import IThumbnailSelectorPort
from module.video_rag.port.transcriber_port import ITranscriberPort, TranscriptionResult
from module.video_rag.service.video_extraction_service import (
    VideoExtractionPipelineService as ExtractVideoMetadataUseCase,
)


@pytest.fixture
def dummy_video_file():
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.write(fd, b"fake video content")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


async def test_extract_video_metadata_use_case_success(dummy_video_file):
    # Mock Media Extractor
    mock_media = AsyncMock(spec=IMediaExtractorPort)
    mock_media.extract_audio.return_value = "/tmp/audio.wav"
    mock_media.get_duration.return_value = 25.5
    mock_media.extract_candidate_frames.return_value = ["/tmp/frame_0001.jpg", "/tmp/frame_0002.jpg"]

    # Mock Transcriber
    mock_transcriber = AsyncMock(spec=ITranscriberPort)
    mock_transcriber.transcribe.return_value = TranscriptionResult(
        full_text="Nội dung kiểm thử phân tích video",
        segments=[
            TranscriptSegment(
                start=0.0,
                end=3.0,
                text="Nội dung kiểm thử",
                speaker="SPEAKER_00",
            ),
            TranscriptSegment(
                start=3.1,
                end=6.0,
                text="phân tích video",
                speaker="SPEAKER_01",
            ),
        ],
        speaker_count=2,
        language="vi",
        duration_seconds=25.5,
    )

    # Mock Thumbnail Selector
    mock_thumbnail = AsyncMock(spec=IThumbnailSelectorPort)
    mock_thumbnail.select_best_frame.return_value = ""

    # Mock LLM
    mock_llm = AsyncMock(spec=ILLMPort)
    mock_llm.enrich_video_metadata.return_value = {
        "caption": "Video kiểm thử triệu view",
        "summary": "Tóm tắt kiểm thử video RAG",
        "hashtag": "#test #viral",
    }

    use_case = ExtractVideoMetadataUseCase(
        media_extractor_port=mock_media,
        transcriber_port=mock_transcriber,
        thumbnail_selector_port=mock_thumbnail,
        llm_port=mock_llm,
    )

    result = await use_case.execute(dummy_video_file, language="vi")

    assert result.video_path == dummy_video_file
    assert result.speaker_count == 2
    assert len(result.transcript_segments) == 2
    assert "SPEAKER_00" in result.transcript_with_speakers
    assert "SPEAKER_01" in result.transcript_with_speakers
    assert result.caption == "Video kiểm thử triệu view"
    assert result.summary == "Tóm tắt kiểm thử video RAG"
    assert result.hashtag == "#test #viral"
    assert result.duration_seconds == 25.5

    mock_media.extract_audio.assert_awaited_once()
    mock_transcriber.transcribe.assert_awaited_once()
    mock_thumbnail.select_best_frame.assert_awaited_once()
    mock_llm.enrich_video_metadata.assert_awaited_once()
