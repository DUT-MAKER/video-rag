"""Integration tests for FFmpegMediaExtractorAdapter."""

import asyncio
import os
import shutil
import tempfile

import pytest

from module.video_rag.infra.media_extractor.ffmpeg_adapter import FFmpegMediaExtractorAdapter

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None, reason="ffmpeg is required for FFmpegMediaExtractorAdapter tests"
)


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp(prefix="test_ffmpeg_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
async def sample_video(temp_dir):
    """Generate a 3-second synthetic MP4 video with sine audio for testing."""
    video_path = os.path.join(temp_dir, "sample.mp4")
    # ffmpeg command to generate test video with audio
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "testsrc=duration=3:size=320x240:rate=25",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=1000:duration=3",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        video_path,
    ]
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await proc.communicate()
    assert os.path.exists(video_path), "Failed to generate sample video"
    return video_path


async def test_ffmpeg_get_duration(sample_video):
    adapter = FFmpegMediaExtractorAdapter()
    duration = await adapter.get_duration(sample_video)
    assert 2.9 <= duration <= 3.1


async def test_ffmpeg_extract_audio(sample_video, temp_dir):
    adapter = FFmpegMediaExtractorAdapter()
    output_audio = os.path.join(temp_dir, "audio.wav")
    result_path = await adapter.extract_audio(sample_video, output_audio)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


async def test_ffmpeg_extract_candidate_frames(sample_video, temp_dir):
    adapter = FFmpegMediaExtractorAdapter()
    frames_dir = os.path.join(temp_dir, "frames")
    frames = await adapter.extract_candidate_frames(sample_video, frames_dir, interval_seconds=1.0)
    assert len(frames) >= 2
    for f in frames:
        assert os.path.exists(f)
