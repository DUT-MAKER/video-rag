"""Shared Faster-Whisper ASR engine reusable by all crawler platforms."""

import os
from typing import Optional

import ctranslate2
from loguru import logger

from module.crawler.domain import TranscriptResult, TranscriptSegment


class WhisperASREngine:
    """Reusable Faster-Whisper ASR engine with safe GPU/CPU auto-detection."""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None

    def _get_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            cuda_count = ctranslate2.get_cuda_device_count()
            device = "cuda" if cuda_count > 0 else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"

            logger.info(
                f"Initializing Faster-Whisper '{self.model_size}' on {device} ({compute_type})"
            )
            self._model = WhisperModel(
                self.model_size, device=device, compute_type=compute_type
            )
        return self._model

    def transcribe(
        self,
        media_path: str,
        video_id: str = "",
    ) -> TranscriptResult:
        """Transcribes local audio or video file into structured timestamped segments."""
        if not os.path.exists(media_path):
            logger.warning(f"[{video_id}] Media file not found for Whisper transcription: {media_path}")
            return TranscriptResult(full_text="", segments=[], is_auto_generated=True)

        try:
            logger.info(f"[{video_id}] Running Whisper transcription on {media_path}...")
            model = self._get_model()
            whisper_segments, _ = model.transcribe(media_path, beam_size=5)

            segments = [
                TranscriptSegment(
                    start=round(float(seg.start), 2),
                    end=round(float(seg.end), 2),
                    text=str(seg.text).strip(),
                )
                for seg in whisper_segments
                if str(seg.text).strip()
            ]
            full_text = " ".join(s.text for s in segments)
            logger.info(f"[{video_id}] Whisper transcription completed ({len(segments)} segments).")
            return TranscriptResult(
                full_text=full_text,
                segments=segments,
                is_auto_generated=True,
            )
        except Exception as e:
            logger.error(f"[{video_id}] Faster-Whisper transcription failed: {e}")
            return TranscriptResult(full_text="", segments=[], is_auto_generated=True)
