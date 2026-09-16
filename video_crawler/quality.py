"""Small synchronous quality gate applied before persistence."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from .domain import CrawledVideo


@dataclass(frozen=True)
class QualityResult:
    accepted: bool
    reasons: tuple[str, ...] = ()


def check_video_quality(video: CrawledVideo) -> QualityResult:
    reasons: list[str] = []
    required = {
        "caption_missing": video.caption,
        "hashtag_missing": video.hashtag,
        "transcript_missing": video.transcript,
        "image_url_missing": video.image_url,
        "summary_missing": video.summary,
        "video_url_missing": video.video_url,
    }
    reasons.extend(key for key, value in required.items() if not value.strip())
    if not video.platform_video_id.strip() or not _valid_http_url(video.canonical_url):
        reasons.append("canonical_identity_missing")
    if any(warning == "ui_contaminated" for warning in video.quality_warnings):
        reasons.append("ui_contaminated")
    return QualityResult(accepted=not reasons, reasons=tuple(reasons))


def _valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
