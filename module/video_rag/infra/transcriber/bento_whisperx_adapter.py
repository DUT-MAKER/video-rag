"""BentoWhisperXAdapter implementation connecting to BentoML STT service."""

import os

import httpx
from loguru import logger

from module.video_rag.domain.entities.extraction_result import TranscriptSegment
from module.video_rag.domain.exceptions import TranscriptionError
from module.video_rag.port.transcriber_port import ITranscriberPort, TranscriptionResult


class BentoWhisperXAdapter(ITranscriberPort):
    """Client adapter connecting to BentoML WhisperX STT & Diarization microservice."""

    def __init__(
        self,
        bento_url: str = "http://localhost:3001",
        timeout: float = 300.0,
    ) -> None:
        self._bento_url = bento_url.rstrip("/")
        self._timeout = timeout

    async def transcribe(
        self,
        audio_path: str,
        language: str = "vi",
        enable_diarization: bool = True,
    ) -> TranscriptionResult:
        """Call remote BentoML STT service to transcribe audio with speaker diarization."""
        if not os.path.exists(audio_path):
            raise TranscriptionError(f"Audio file not found: {audio_path}")

        endpoint = f"{self._bento_url}/transcribe"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                with open(audio_path, "rb") as f:
                    files = {"audio": (os.path.basename(audio_path), f, "audio/wav")}
                    data = {
                        "language": language,
                        "enable_diarization": str(enable_diarization).lower(),
                    }
                    response = await client.post(endpoint, files=files, data=data)

                if response.status_code == 200:
                    payload = response.json()
                    segments = [
                        TranscriptSegment(
                            start=float(seg.get("start", 0.0)),
                            end=float(seg.get("end", 0.0)),
                            text=str(seg.get("text", "")),
                            speaker=str(seg.get("speaker", "SPEAKER_00")),
                        )
                        for seg in payload.get("segments", [])
                    ]
                    return TranscriptionResult(
                        full_text=str(payload.get("full_text", "")),
                        segments=segments,
                        speaker_count=int(payload.get("speaker_count", 1)),
                        language=str(payload.get("language", language)),
                        duration_seconds=float(payload.get("duration_seconds", 0.0)),
                    )
        except Exception as exc:
            raise TranscriptionError(f"BentoML STT service call failed: {exc}") from exc
