"""Unit tests for BentoWhisperXAdapter."""

import os
import tempfile

import pytest

from module.video_rag.domain.exceptions import TranscriptionError
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


async def test_bento_whisperx_remote_failure(dummy_audio_file):
    # Testing when remote BentoML server is offline or fails
    adapter = BentoWhisperXAdapter(
        bento_url="http://localhost:9999",  # non-existent port
    )
    with pytest.raises(TranscriptionError):
        await adapter.transcribe(dummy_audio_file, language="vi")


async def test_bento_whisperx_file_not_found():
    adapter = BentoWhisperXAdapter()
    with pytest.raises(TranscriptionError):
        await adapter.transcribe("/non/existent/path.wav")
