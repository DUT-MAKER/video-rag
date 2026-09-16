from pathlib import Path

import pytest

from video_crawler.infrastructure.media import YtDlpMediaResolver


def test_normalizes_yt_dlp_engagement_metrics() -> None:
    assert YtDlpMediaResolver._metrics(
        {
            "view_count": 1000,
            "like_count": 90,
            "comment_count": 12,
            "repost_count": 7,
            "share_count": None,
        }
    ) == {
        "view_count": 1000,
        "like_count": 90,
        "comment_count": 12,
        "share_count": 7,
    }


def test_thumbnail_falls_back_to_ffmpeg_frame(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> None:
        calls.append(command)

    monkeypatch.setattr("video_crawler.infrastructure.media.subprocess.run", fake_run)
    output = YtDlpMediaResolver._extract_frame(tmp_path / "video.mp4", tmp_path)

    assert output == tmp_path / "thumbnail.jpg"
    assert calls[0][0] == "ffmpeg"
