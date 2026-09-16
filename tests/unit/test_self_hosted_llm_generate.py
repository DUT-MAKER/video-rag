"""Unit tests for SelfHostedLLMAdapter generate_script with streaming and logging."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from loguru import logger

from module.video_rag.domain.value_objects.platform_target import PlatformTarget
from module.video_rag.infra.llm.self_hosted_llm import SelfHostedLLMAdapter


class FakeDelta:
    def __init__(self, content: str | None = None, reasoning_content: str | None = None) -> None:
        self.content = content
        self.reasoning_content = reasoning_content


class FakeChoice:
    def __init__(self, delta: FakeDelta) -> None:
        self.delta = delta


class FakeChunk:
    def __init__(self, delta: FakeDelta) -> None:
        self.choices = [FakeChoice(delta)]


async def _fake_stream_chunks(json_str: str, has_reasoning: bool = False):
    if has_reasoning:
        yield FakeChunk(FakeDelta(reasoning_content="Thinking about viral hooks..."))
    # Yield character or slice chunks to simulate streaming
    step = 15
    for i in range(0, len(json_str), step):
        yield FakeChunk(FakeDelta(content=json_str[i : i + step]))


@pytest.mark.asyncio
async def test_self_hosted_llm_generate_script_streaming_and_logging() -> None:
    adapter = SelfHostedLLMAdapter(
        api_base_url="http://localhost:8000/v1",
        api_key="test-key",
        model_name="test-model",
    )

    sample_script = {
        "title": "5 Bí Quyết Tăng Năng Suất 10X",
        "target_niche": "Sinh viên và người đi làm",
        "target_duration_seconds": 45,
        "hook": {
            "hook_type": "contrarian",
            "script": "Dừng ngay việc dậy từ 4h sáng nếu bạn muốn thành công!",
            "visual_action": "Cảnh nhân vật tắt chuông báo thức trong phòng tối",
            "retention_rationale": "Phá vỡ niềm tin phổ biến để giữ chân người xem",
            "duration_seconds": 4,
        },
        "scenes": [
            {
                "scene_number": 1,
                "time_range": "00:00 - 00:04",
                "narration": "Dừng ngay việc dậy từ 4h sáng!",
                "visual_action": "Cận cảnh tắt báo thức",
                "image_prompt": "Cinematic dark bedroom lighting",
                "video_prompt": "Camera tracking shot",
                "audio_sfx_cue": "Alarm sound fade out",
            }
        ],
        "call_to_action": {
            "script": "Follow kênh để nhận cẩm nang làm việc hiệu quả!",
            "visual_cue": "Biểu tượng follow nhấp nháy",
        },
        "suggested_hashtags": ["#nangsuat", "#phattrienbanthan"],
    }
    json_payload = json.dumps(sample_script, ensure_ascii=False)

    logged_messages: list[str] = []
    sink_id = logger.add(lambda msg: logged_messages.append(str(msg)))

    try:
        mock_create = AsyncMock(return_value=_fake_stream_chunks(json_payload, has_reasoning=True))
        with patch.object(adapter._client.chat.completions, "create", mock_create):
            script = await adapter.generate_script(
                topic="Năng suất làm việc 10X",
                target_audience="Người đi làm",
                duration_seconds=45,
                platform=PlatformTarget.TIKTOK,
                hook_style="contrarian",
                reference_contexts=[],
            )

        assert script.title == "5 Bí Quyết Tăng Năng Suất 10X"
        assert script.hook.script == "Dừng ngay việc dậy từ 4h sáng nếu bạn muốn thành công!"
        assert len(script.scenes) == 1
        assert script.platform == PlatformTarget.TIKTOK

        # Check that thinking stream was logged
        all_logs = "".join(logged_messages)
        assert "Thinking about viral hooks..." in all_logs
    finally:
        logger.remove(sink_id)
