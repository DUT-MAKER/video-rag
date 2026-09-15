"""Unit tests for domain entities and value objects."""

from module.video_rag.domain.entities.reference_pattern import ReferencedPattern
from module.video_rag.domain.entities.video_record import RawVideoRecord
from module.video_rag.domain.entities.viral_script import CallToAction, Hook, Scene, ViralScript
from module.video_rag.domain.value_objects.hook_type import HookType
from module.video_rag.domain.value_objects.platform_target import PlatformTarget


def test_raw_video_record_hook_extraction() -> None:
    """Verify 3-5s opening hook extraction logic from transcript."""
    record = RawVideoRecord(
        caption="Sample Title",
        hashtag="#viral",
        transcript="90% of people fail when building new habits because of this mistake! Apply the 2-minute rule.",
        image_url="https://minio/thumb.jpg",
        summary="Video summary",
        video_url="https://minio/video.mp4",
    )

    hook = record.extract_hook()
    assert "90% of people fail" in hook
    assert record.id != ""


def test_raw_video_record_to_searchable_text() -> None:
    """Verify rich text composition for semantic vector embedding."""
    record = RawVideoRecord(
        caption="Learn How to Say NO",
        hashtag="#skills",
        transcript="Saying no protects your most valuable asset: time.",
        image_url="",
        summary="Polite decline frameworks.",
        video_url="",
    )

    searchable = record.to_searchable_text()
    assert "Title: Learn How to Say NO" in searchable
    assert "Summary: Polite decline frameworks." in searchable
    assert "Transcript: Saying no protects your" in searchable


def test_viral_script_entity_serialization() -> None:
    """Verify serialization structure and values of ViralScript entity."""
    hook = Hook(
        hook_type=HookType.SHOCKING_FACT,
        script="99% of AI users are doing this completely wrong!",
        visual_action="Camera zooms sharply into computer monitor displaying flashing red alert.",
        retention_rationale="Exploits fear of missing out and hidden operational failures.",
        duration_seconds=4,
    )
    scenes = [
        Scene(
            scene_number=1,
            time_range="00:00 - 00:04",
            narration="99% of AI users are doing this completely wrong!",
            visual_action="Intense zoom in",
            image_prompt="A dramatic red warning screen with neon lights",
            video_prompt="Fast camera dolly into monitor",
            audio_sfx_cue="Glitch buzz",
        )
    ]
    cta = CallToAction(
        script="Follow for more cutting-edge AI breakdowns!",
        visual_cue="Pulsing follow button animation",
    )
    references = [
        ReferencedPattern(
            original_caption="Benchmark AI Video",
            matched_hook="Stop right now if you...",
            minio_video_url="https://minio/ref.mp4",
            similarity_score=0.92,
        )
    ]

    script = ViralScript(
        title="Fatal Mistakes When Using AI",
        target_niche="Tech & AI Creators",
        platform=PlatformTarget.TIKTOK,
        target_duration_seconds=45,
        hook=hook,
        scenes=scenes,
        call_to_action=cta,
        references=references,
    )

    data = script.to_dict()
    assert data["title"] == "Fatal Mistakes When Using AI"
    assert data["platform"] == "tiktok"
    assert data["hook"]["hook_type"] == "shocking_fact"
    assert len(data["scenes"]) == 1
    assert data["references"][0]["similarity_score"] == 0.92
