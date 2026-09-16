"""Unit tests for BentoWhisperXAdapter."""

import os
import tempfile
import pytest

from module.video_rag.infra.transcriber.bento_whisperx_adapter import (
    BentoWhisperXAdapter,
)


@pytest.fixture
def dummy_audio_file():
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.write(fd, b"RIFF....WAVEfmt ....data....")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


async def test_bento_whisperx_fallback_mode(dummy_audio_file):
    # Testing fallback mode when remote BentoML server is offline
    adapter = BentoWhisperXAdapter(
        bento_url="http://localhost:9999",  # non-existent port
        fallback_mode=True,
    )
    result = await adapter.transcribe(dummy_audio_file, language="vi")

    assert result.speaker_count == 2
    assert len(result.segments) == 4
    assert result.segments[0].speaker == "SPEAKER_00"
    assert result.segments[1].speaker == "SPEAKER_01"
    assert "90% mọi người thất bại" in result.full_text
    assert result.language == "vi"
    assert result.duration_seconds > 0


async def test_bento_whisperx_file_not_found():
    adapter = BentoWhisperXAdapter(fallback_mode=False)
    with pytest.raises(Exception):
        await adapter.transcribe("/non/existent/path.wav")
