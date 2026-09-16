"""Anchor test for BentoML WhisperXService."""

import os
import tempfile
import pytest

from services.stt_service.service import WhisperXService


@pytest.fixture
def dummy_audio_file():
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.write(fd, b"RIFF....WAVEfmt ....data....")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


def test_whisperx_service_direct_call(dummy_audio_file):
    """Test calling the service method directly in Python."""
    import pathlib

    service = WhisperXService()
    result = service.transcribe(
        audio=pathlib.Path(dummy_audio_file),
        language="vi",
        enable_diarization=True,
    )

    assert result.speaker_count == 2
    assert len(result.segments) == 4
    assert result.segments[0].speaker == "SPEAKER_00"
    assert result.segments[1].speaker == "SPEAKER_01"
    assert "90% mọi người thất bại" in result.full_text
