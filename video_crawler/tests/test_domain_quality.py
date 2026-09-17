from datetime import UTC, datetime

import pytest

from video_crawler.domain import CrawlJobRequest, CrawledVideo, DiscoveryMethod, Platform
from video_crawler.quality import check_video_quality


def complete_video() -> CrawledVideo:
    return CrawledVideo(
        platform=Platform.YOUTUBE,
        platform_video_id="abc123",
        canonical_url="https://youtube.com/watch?v=abc123",
        caption="A useful video",
        hashtag="#youtube",
        image_url="https://minio/media/thumb.jpg",
        video_url="https://minio/media/video.mp4",
        published_at=datetime.now(UTC),
    )


def test_quality_accepts_complete_video() -> None:
    assert check_video_quality(complete_video()).accepted is True


def test_quality_rejects_missing_fields_and_ui_contamination() -> None:
    video = complete_video()
    video.image_url = ""
    video.quality_warnings.append("ui_contaminated")
    result = check_video_quality(video)
    assert result.accepted is False
    assert set(result.reasons) == {"image_url_missing", "ui_contaminated"}


def test_source_url_request_requires_each_platform_url() -> None:
    with pytest.raises(ValueError, match="Missing source URL"):
        CrawlJobRequest(
            platforms=(Platform.FACEBOOK, Platform.TIKTOK),
            discovery_method=DiscoveryMethod.SOURCE_URL,
            source_urls={Platform.FACEBOOK: "https://facebook.com/reel/1"},
        )
