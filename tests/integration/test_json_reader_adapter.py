"""Integration tests for JsonDataReaderAdapter."""

from src.infra.data_readers.json_reader_adapter import JsonDataReaderAdapter


def test_read_real_sample_viral_videos_file() -> None:
    """Verify reading actual sample file data/samples/sample_viral_videos.json."""
    adapter = JsonDataReaderAdapter()
    file_path = "data/samples/sample_viral_videos.json"

    records = adapter.read_from_file(file_path)
    assert len(records) == 5

    # Check first record mapping
    first = records[0]
    assert "21 ngày" in first.caption or "thói quen" in first.caption
    assert "https://minio.example.com" in first.video_url
    assert "https://minio.example.com" in first.image_url
    assert first.extract_hook() != ""
    assert first.id != ""


def test_read_from_records_dict_list() -> None:
    """Verify reading from raw dictionary list with dataset-specific keys."""
    adapter = JsonDataReaderAdapter()
    raw_list = [
        {
            "caption": "Test video",
            "hastag": ["#test1", "#test2"],
            "trancsript": "This is a fast-paced opening test transcript.",
            "hình ảnh": "https://img.jpg",
            "nội dung tóm tắt": "Test summary",
            "url_video": "https://vid.mp4",
        }
    ]

    records = adapter.read_from_records(raw_list)
    assert len(records) == 1
    assert records[0].caption == "Test video"
    assert "#test1 #test2" in records[0].hashtag
    assert records[0].transcript == "This is a fast-paced opening test transcript."
    assert records[0].image_url == "https://img.jpg"


def test_read_from_standard_english_records() -> None:
    """Verify reading from dictionary list with standard English keys."""
    adapter = JsonDataReaderAdapter()
    raw_list = [
        {
            "caption": "English Test Video",
            "hashtag": "#productivity #focus",
            "transcript": "Stop wasting time on low priority tasks.",
            "image_url": "https://img.jpg",
            "summary": "Time management frameworks.",
            "video_url": "https://vid.mp4",
        }
    ]

    records = adapter.read_from_records(raw_list)
    assert len(records) == 1
    assert records[0].caption == "English Test Video"
    assert records[0].hashtag == "#productivity #focus"
    assert records[0].transcript == "Stop wasting time on low priority tasks."
    assert records[0].summary == "Time management frameworks."
