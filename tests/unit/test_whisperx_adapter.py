"""Unit tests for WhisperXTranscriberAdapter."""

import os
import tempfile
import pytest

from module.video_rag.infra.transcriber.whisperx_adapter import (
    WhisperXTranscriberAdapter,
)


@pytest.fixture
def dummy_audio_file():
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.write(fd, b"RIFF....WAVEfmt ....data....")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


async def test_whisperx_fallback_transcription(dummy_audio_file):
    adapter = WhisperXTranscriberAdapter(fallback_mode=True)
    result = await adapter.transcribe(dummy_audio_file, language="vi")

    assert len(result.segments) == 4
    assert result.speaker_count == 2
    assert result.segments[0].speaker == "SPEAKER_00"
    assert result.segments[1].speaker == "SPEAKER_01"
    assert "90% mọi người thất bại" in result.full_text
    assert result.language == "vi"
    assert result.duration_seconds > 0


async def test_whisperx_file_not_found():
    adapter = WhisperXTranscriberAdapter(fallback_mode=False)
    with pytest.raises(Exception):
        await adapter.transcribe("/non/existent/audio.wav")
