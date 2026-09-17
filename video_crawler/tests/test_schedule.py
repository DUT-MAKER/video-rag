from datetime import datetime, timezone

import pytest

from video_crawler.domain import Platform
from video_crawler.schedule import ScheduleConfig, due_slot


def test_four_daily_slots_rotate_topics_and_platforms() -> None:
    config = ScheduleConfig.from_dict({
        "timezone": "Asia/Ho_Chi_Minh",
        "hours": [22, 0, 2, 4],
        "keywords": ["food", "travel", "fitness"],
        "links_per_platform": 10,
    })
    at_midnight = datetime(2026, 9, 16, 17, 0, tzinfo=timezone.utc)
    facebook = due_slot(config, Platform.FACEBOOK, at_midnight)
    tiktok = due_slot(config, Platform.TIKTOK, at_midnight)

    assert facebook is not None and facebook.key.endswith(":00:facebook")
    assert tiktok is not None and tiktok.keyword != facebook.keyword
    assert due_slot(config, Platform.FACEBOOK, at_midnight.replace(minute=31)) is None


def test_schedule_rejects_empty_and_duplicate_keywords() -> None:
    with pytest.raises(ValueError):
        ScheduleConfig.from_dict({"keywords": ["food", " food "]})


def test_scheduled_request_round_trip_keeps_new_link_limit() -> None:
    from video_crawler.domain import CrawlJobRequest, DiscoveryMethod

    request = CrawlJobRequest(
        (Platform.FACEBOOK,), DiscoveryMethod.KEYWORD, query="food",
        max_items_per_platform=100, max_new_links=10,
    )
    assert CrawlJobRequest.from_dict(request.to_dict()).max_new_links == 10
