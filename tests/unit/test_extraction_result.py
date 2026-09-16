"""Unit tests for VideoExtractionResult domain entity."""

from module.video_rag.domain.entities.extraction_result import (
    TranscriptSegment,
    VideoExtractionResult,
)


def test_transcript_segment_creation() -> None:
    segment = TranscriptSegment(
        start=0.0,
        end=4.5,
        text="Xin chào tất cả mọi người",
        speaker="SPEAKER_00",
    )
    assert segment.start == 0.0
    assert segment.end == 4.5
    assert segment.text == "Xin chào tất cả mọi người"
    assert segment.speaker == "SPEAKER_00"


def test_video_extraction_result_format_speaker_transcript() -> None:
    result = VideoExtractionResult(
        video_path="/data/videos/test.mp4",
        transcript="Xin chào mọi người. Tôi là chuyên gia.",
        transcript_with_speakers="",
        transcript_segments=[
            TranscriptSegment(
                start=0.0,
                end=2.5,
                text="Xin chào mọi người.",
                speaker="SPEAKER_00",
            ),
            TranscriptSegment(
                start=2.6,
                end=5.0,
                text="Tôi là chuyên gia.",
                speaker="SPEAKER_01",
            ),
        ],
        speaker_count=2,
    )

    formatted = result.format_speaker_transcript()
    assert "SPEAKER_00 [0.0s -> 2.5s]: Xin chào mọi người." in formatted
    assert "SPEAKER_01 [2.6s -> 5.0s]: Tôi là chuyên gia." in formatted


def test_video_extraction_result_to_raw_video_record() -> None:
    result = VideoExtractionResult(
        video_path="/data/videos/test.mp4",
        transcript="Nội dung video ngắn",
        transcript_with_speakers="SPEAKER_00 [0.0s -> 3.0s]: Nội dung video ngắn",
        caption="Cách làm video triệu view",
        hashtag="#viral #shortform",
        summary="Tóm tắt video hướng dẫn làm video viral",
        thumbnail_path="/tmp/thumb.jpg",
        duration_seconds=30.0,
    )

    record = result.to_raw_video_record(
        video_url="https://s3.example.com/videos/test.mp4",
        image_url="https://s3.example.com/thumbs/thumb.jpg",
    )

    assert record.caption == "Cách làm video triệu view"
    assert record.hashtag == "#viral #shortform"
    assert record.transcript == "SPEAKER_00 [0.0s -> 3.0s]: Nội dung video ngắn"
    assert record.image_url == "https://s3.example.com/thumbs/thumb.jpg"
    assert record.video_url == "https://s3.example.com/videos/test.mp4"
    assert record.summary == "Tóm tắt video hướng dẫn làm video viral"
