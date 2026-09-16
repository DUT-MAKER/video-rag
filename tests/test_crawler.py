"""Unit tests for the Multi-Platform Video Crawler pipeline using mock ports."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from module.crawler.domain import (
    DownloadedMedia,
    IpBlockedStopSignal,
    LLMUnavailableError,
    PlatformType,
    TranscriptResult,
    TranscriptSegment,
    VideoMetadata,
)
from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled

from module.crawler.platforms.youtube_shorts.pipeline import YouTubeShortsPipeline
from module.crawler.platforms.youtube_shorts.transcript import YouTubeShortsTranscriptAdapter
from module.crawler.shared.dedup_store import JsonFileDedupStore
from module.crawler.shared.storage import LocalStorageAdapter


@pytest.fixture
def mock_ports():
    extractor = MagicMock()
    transcriber = MagicMock()
    storage = MagicMock()
    summarizer = MagicMock()
    dedup_store = MagicMock()
    return extractor, transcriber, storage, summarizer, dedup_store


def test_pipeline_happy_path(mock_ports, tmp_path):
    extractor, transcriber, storage, summarizer, dedup_store = mock_ports

    dedup_store.is_processed.return_value = False

    dummy_video = tmp_path / "test_vid.mp4"
    dummy_video.write_bytes(b"fake video data")
    dummy_thumb = tmp_path / "test_vid.jpg"
    dummy_thumb.write_bytes(b"fake image data")

    extractor.fetch_metadata.return_value = VideoMetadata(
        video_id="abc12345678",
        platform=PlatformType.YOUTUBE_SHORTS,
        title="Test Shorts Title",
        description="Check this out #shorts #viral",
        caption="Test Shorts Title\nCheck this out #shorts #viral",
        hashtags=["shorts", "viral"],
        duration=35.0,
        width=1080,
        height=1920,
        view_count=50000,
        like_count=2000,
        comment_count=120,
        upload_date="20260315",
        is_shorts=True,
    )
    extractor.download_media.return_value = DownloadedMedia(
        video_path=str(dummy_video),
        thumbnail_path=str(dummy_thumb),
    )

    transcriber.extract_transcript.return_value = TranscriptResult(
        full_text="Xin chào các bạn đến với video viral",
        segments=[TranscriptSegment(start=0.0, end=2.5, text="Xin chào các bạn đến với video viral")],
        is_auto_generated=False,
    )

    storage.upload_file.side_effect = lambda local_p, dest: f"http://storage.local/{dest}"
    summarizer.summarize.return_value = "Video chia sẻ bí quyết tạo kịch bản viral."

    pipeline = YouTubeShortsPipeline(
        extractor=extractor,
        transcriber=transcriber,
        storage=storage,
        summarizer=summarizer,
        dedup_store=dedup_store,
    )

    result = pipeline.process_video("abc12345678")

    assert result is not None
    # Verify PRD Data Contract
    assert result["caption"] == "Test Shorts Title\nCheck this out #shorts #viral"
    assert result["hashtag"] == ["shorts", "viral"]
    assert result["transcript"] == "Xin chào các bạn đến với video viral"
    assert result["video_url"] == "http://storage.local/videos/abc12345678.mp4"
    assert result["image_url"] == "http://storage.local/thumbnails/abc12345678.jpg"
    assert result["summary"] == "Video chia sẻ bí quyết tạo kịch bản viral."

    # Verify Enriched Metadata
    meta = result["_enriched_metadata"]
    assert meta["platform"] == "youtube_shorts"
    assert meta["video_id"] == "abc12345678"
    assert meta["duration"] == 35.0
    assert meta["is_auto_generated"] is False
    assert meta["metrics"]["view_count"] == 50000
    assert len(meta["transcript_segments"]) == 1

    dedup_store.mark_processed.assert_called_once_with("abc12345678")


def test_pipeline_skips_already_processed_video(mock_ports):
    extractor, transcriber, storage, summarizer, dedup_store = mock_ports
    dedup_store.is_processed.return_value = True

    pipeline = YouTubeShortsPipeline(extractor, transcriber, storage, summarizer, dedup_store)
    result = pipeline.process_video("abc12345678")

    assert result is None
    extractor.fetch_metadata.assert_not_called()
    extractor.download_media.assert_not_called()


def test_pipeline_skips_non_shorts(mock_ports):
    extractor, transcriber, storage, summarizer, dedup_store = mock_ports
    dedup_store.is_processed.return_value = False

    extractor.fetch_metadata.return_value = VideoMetadata(
        video_id="long1234567",
        platform=PlatformType.YOUTUBE_SHORTS,
        title="Long Video",
        description="",
        caption="Long Video",
        hashtags=[],
        duration=120.0,
        width=1920,
        height=1080,
        view_count=1000,
        like_count=50,
        comment_count=5,
        upload_date="20260101",
        is_shorts=False,
    )

    pipeline = YouTubeShortsPipeline(extractor, transcriber, storage, summarizer, dedup_store)
    result = pipeline.process_video("long1234567")

    assert result is None
    extractor.download_media.assert_not_called()


def test_pipeline_reraises_ip_blocked_signal(mock_ports, tmp_path):
    extractor, transcriber, storage, summarizer, dedup_store = mock_ports
    dedup_store.is_processed.return_value = False

    dummy_video = tmp_path / "test.mp4"
    dummy_video.write_bytes(b"data")

    extractor.fetch_metadata.return_value = VideoMetadata(
        video_id="blocked1234",
        platform=PlatformType.YOUTUBE_SHORTS,
        title="Shorts",
        description="",
        caption="Shorts",
        hashtags=[],
        duration=20.0,
        width=1080,
        height=1920,
        view_count=100,
        like_count=10,
        comment_count=1,
        upload_date="20260101",
        is_shorts=True,
    )
    extractor.download_media.return_value = DownloadedMedia(
        video_path=str(dummy_video), thumbnail_path=None
    )

    transcriber.extract_transcript.side_effect = IpBlockedStopSignal("IP blocked by YouTube")

    pipeline = YouTubeShortsPipeline(extractor, transcriber, storage, summarizer, dedup_store)

    with pytest.raises(IpBlockedStopSignal):
        pipeline.process_video("blocked1234")


def test_pipeline_handles_llm_unavailable_without_fabrication(mock_ports, tmp_path):
    extractor, transcriber, storage, summarizer, dedup_store = mock_ports
    dedup_store.is_processed.return_value = False

    dummy_video = tmp_path / "test.mp4"
    dummy_video.write_bytes(b"data")

    extractor.fetch_metadata.return_value = VideoMetadata(
        video_id="testllm1234",
        platform=PlatformType.YOUTUBE_SHORTS,
        title="Shorts",
        description="",
        caption="Shorts",
        hashtags=[],
        duration=20.0,
        width=1080,
        height=1920,
        view_count=100,
        like_count=10,
        comment_count=1,
        upload_date="20260101",
        is_shorts=True,
    )
    extractor.download_media.return_value = DownloadedMedia(
        video_path=str(dummy_video), thumbnail_path=None
    )
    transcriber.extract_transcript.return_value = TranscriptResult(
        full_text="Test speech", segments=[], is_auto_generated=True
    )
    storage.upload_file.return_value = "http://storage.local/video.mp4"
    
    summarizer.summarize.side_effect = LLMUnavailableError("Connection refused")

    pipeline = YouTubeShortsPipeline(extractor, transcriber, storage, summarizer, dedup_store)
    result = pipeline.process_video("testllm1234")

    assert result is not None
    assert result["summary"] is None


def test_local_storage_adapter(tmp_path):
    adapter = LocalStorageAdapter(base_dir=str(tmp_path / "storage"))
    dummy = tmp_path / "sample.mp4"
    dummy.write_bytes(b"video contents")

    stored_path = adapter.upload_file(str(dummy), "videos/test.mp4")
    assert Path(stored_path).exists()
    assert Path(stored_path).read_bytes() == b"video contents"


def test_json_file_dedup_store(tmp_path):
    manifest = tmp_path / "manifest.json"
    store = JsonFileDedupStore(manifest_path=str(manifest))

    assert not store.is_processed("vid001")
    store.mark_processed("vid001")
    assert store.is_processed("vid001")

    store_reloaded = JsonFileDedupStore(manifest_path=str(manifest))
    assert store_reloaded.is_processed("vid001")
    assert not store_reloaded.is_processed("vid002")


def test_transcript_adapter_whisper_fallback_when_no_subtitles():
    """Verify YouTubeShortsTranscriptAdapter falls back to Whisper when NoTranscriptFound occurs."""
    adapter = YouTubeShortsTranscriptAdapter(whisper_model_size="base")
    adapter._api = MagicMock()
    adapter._api.list.side_effect = NoTranscriptFound("nosub123", ["vi", "en"], None)

    adapter.whisper_engine = MagicMock()
    expected_whisper_res = TranscriptResult(
        full_text="Lời thoại bóc tách tự động bằng Whisper ASR",
        segments=[
            TranscriptSegment(start=0.0, end=3.5, text="Lời thoại bóc tách tự động bằng Whisper ASR")
        ],
        is_auto_generated=True,
    )
    adapter.whisper_engine.transcribe.return_value = expected_whisper_res

    res = adapter.extract_transcript("nosub123", local_media_path="/tmp/fake_audio.mp4")

    adapter.whisper_engine.transcribe.assert_called_once_with("/tmp/fake_audio.mp4", video_id="nosub123")
    assert res.full_text == "Lời thoại bóc tách tự động bằng Whisper ASR"
    assert res.is_auto_generated is True
    assert len(res.segments) == 1
    assert res.segments[0].text == "Lời thoại bóc tách tự động bằng Whisper ASR"


def test_transcript_adapter_whisper_fallback_when_transcripts_disabled():
    """Verify YouTubeShortsTranscriptAdapter falls back to Whisper when TranscriptsDisabled occurs."""
    adapter = YouTubeShortsTranscriptAdapter(whisper_model_size="base")
    adapter._api = MagicMock()
    adapter._api.list.side_effect = TranscriptsDisabled("disabled123")

    adapter.whisper_engine = MagicMock()
    expected_whisper_res = TranscriptResult(
        full_text="Giọng nói từ video tắt phụ đề",
        segments=[TranscriptSegment(start=0.0, end=2.0, text="Giọng nói từ video tắt phụ đề")],
        is_auto_generated=True,
    )
    adapter.whisper_engine.transcribe.return_value = expected_whisper_res

    res = adapter.extract_transcript("disabled123", local_media_path="/tmp/fake_disabled.mp4")

    adapter.whisper_engine.transcribe.assert_called_once_with("/tmp/fake_disabled.mp4", video_id="disabled123")
    assert res.full_text == "Giọng nói từ video tắt phụ đề"
    assert res.is_auto_generated is True


def test_pipeline_asr_fallback_when_no_transcript(mock_ports, tmp_path):
    """Verify pipeline integrates transcript from Whisper fallback and propagates metadata."""
    extractor, transcriber, storage, summarizer, dedup_store = mock_ports
    dedup_store.is_processed.return_value = False

    dummy_video = tmp_path / "nosub.mp4"
    dummy_video.write_bytes(b"video bytes")

    extractor.fetch_metadata.return_value = VideoMetadata(
        video_id="nosub_vid",
        platform=PlatformType.YOUTUBE_SHORTS,
        title="Video không có phụ đề trực tuyến",
        description="",
        caption="Video không có phụ đề trực tuyến",
        hashtags=["shorts"],
        duration=25.0,
        width=1080,
        height=1920,
        view_count=5000,
        like_count=200,
        comment_count=10,
        upload_date="20260316",
        is_shorts=True,
    )
    extractor.download_media.return_value = DownloadedMedia(
        video_path=str(dummy_video), thumbnail_path=None
    )

    whisper_transcript = TranscriptResult(
        full_text="Hook bóc tách bởi Whisper: Bí quyết nấu ăn ngon",
        segments=[TranscriptSegment(start=0.0, end=3.5, text="Hook bóc tách bởi Whisper: Bí quyết nấu ăn ngon")],
        is_auto_generated=True,
    )
    transcriber.extract_transcript.return_value = whisper_transcript
    storage.upload_file.return_value = "http://storage.local/videos/nosub_vid.mp4"
    summarizer.summarize.return_value = "Tóm tắt video nấu ăn."

    pipeline = YouTubeShortsPipeline(extractor, transcriber, storage, summarizer, dedup_store)
    result = pipeline.process_video("nosub_vid")

    assert result is not None
    assert result["transcript"] == "Hook bóc tách bởi Whisper: Bí quyết nấu ăn ngon"
    assert result["_enriched_metadata"]["is_auto_generated"] is True
    assert result["_enriched_metadata"]["transcript_segments"][0]["text"] == "Hook bóc tách bởi Whisper: Bí quyết nấu ăn ngon"
    assert result["_enriched_metadata"]["transcript_segments"][0]["start"] == 0.0

