"""FFmpegMediaExtractorAdapter implementation."""

import asyncio
import os
from pathlib import Path

from module.video_rag.domain.exceptions import MediaExtractionError
from module.video_rag.port.media_extractor_port import IMediaExtractorPort


class FFmpegMediaExtractorAdapter(IMediaExtractorPort):
    """Media extraction adapter powered by FFmpeg and FFprobe CLI."""

    def __init__(
        self,
        ffmpeg_path: str = "ffmpeg",
        ffprobe_path: str = "ffprobe",
    ) -> None:
        self._ffmpeg = ffmpeg_path
        self._ffprobe = ffprobe_path

    async def extract_audio(
        self,
        video_path: str,
        output_path: str,
    ) -> str:
        """Extract audio stream from video as 16kHz mono WAV file."""
        if not os.path.exists(video_path):
            raise MediaExtractionError(f"Video file not found: {video_path}")

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        cmd = [
            self._ffmpeg,
            "-y",
            "-i",
            video_path,
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            output_path,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            raise MediaExtractionError(
                f"FFmpeg audio extraction failed (exit {proc.returncode}): {error_msg}"
            )

        return output_path

    async def extract_candidate_frames(
        self,
        video_path: str,
        output_dir: str,
        interval_seconds: float = 2.0,
    ) -> list[str]:
        """Extract candidate keyframes at regular intervals."""
        if not os.path.exists(video_path):
            raise MediaExtractionError(f"Video file not found: {video_path}")

        os.makedirs(output_dir, exist_ok=True)

        fps_val = 1.0 / max(interval_seconds, 0.1)
        output_pattern = os.path.join(output_dir, "frame_%04d.jpg")

        cmd = [
            self._ffmpeg,
            "-y",
            "-i",
            video_path,
            "-vf",
            f"fps={fps_val}",
            "-q:v",
            "2",
            output_pattern,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            raise MediaExtractionError(
                f"FFmpeg frame extraction failed (exit {proc.returncode}): {error_msg}"
            )

        frame_files = sorted(Path(output_dir).glob("frame_*.jpg"))
        return [str(p) for p in frame_files]

    async def get_duration(self, video_path: str) -> float:
        """Get video duration in seconds using ffprobe."""
        if not os.path.exists(video_path):
            raise MediaExtractionError(f"Video file not found: {video_path}")

        cmd = [
            self._ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            raise MediaExtractionError(
                f"FFprobe duration probe failed (exit {proc.returncode}): {error_msg}"
            )

        try:
            raw_duration = stdout.decode("utf-8").strip()
            return float(raw_duration)
        except (ValueError, TypeError) as exc:
            raise MediaExtractionError(
                f"Failed to parse video duration from ffprobe: {exc}"
            ) from exc
