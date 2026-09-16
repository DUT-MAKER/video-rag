"""Subtitle-first transcript extraction with local Whisper fallback."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

from faster_whisper import WhisperModel

from video_crawler.config import CrawlerSettings
from video_crawler.domain import MediaArtifact


class SubtitleWhisperTranscriptProvider:
    def __init__(self, settings: CrawlerSettings) -> None:
        self.settings = settings
        self._model: WhisperModel | None = None

    async def transcribe(self, artifact: MediaArtifact) -> str:
        for subtitle in artifact.subtitle_paths:
            text = self._read_vtt(Path(subtitle))
            if text:
                return text
        return await asyncio.to_thread(self._whisper, artifact.video_path)

    @staticmethod
    def _read_vtt(path: Path) -> str:
        content = path.read_text(encoding="utf-8", errors="ignore")
        lines: list[str] = []
        previous = ""
        for raw in content.splitlines():
            line = re.sub(r"<[^>]+>", "", raw).strip()
            if not line or line == "WEBVTT" or "-->" in line or line.isdigit():
                continue
            if line != previous:
                lines.append(line)
                previous = line
        return " ".join(lines).strip()

    def _whisper(self, video_path: str) -> str:
        if self._model is None:
            self._model = WhisperModel(
                self.settings.whisper_model,
                device=self.settings.whisper_device,
                compute_type=self.settings.whisper_compute_type,
            )
        segments, _ = self._model.transcribe(video_path, vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments if segment.text.strip()).strip()
