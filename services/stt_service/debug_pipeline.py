"""CLI Debug Tool for WhisperX STT + Diarization Service.

Calls WhisperXService directly (using the exact same implementation as BentoML)
and outputs a multi-track visual timeline chart and JSON inspection report.

Usage:
    uv run python services/stt_service/debug_pipeline.py --audio /path/to/audio.mp3
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from loguru import logger

from services.stt_service.service import WhisperXService


def run_debug(
    audio_path: str,
    output_dir: str = "./debug_output",
    language: str = "vi",
    enable_diarization: bool = True,
) -> dict:
    """Run WhisperXService with debug chart export."""
    out_dir = pathlib.Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    chart_file = str(out_dir / "debug_pipeline_timeline.png")

    logger.info("=" * 60)
    logger.info("STARTING DEBUG TEST RUN VIA WHISPERX SERVICE")
    logger.info(f"Input Audio  : {audio_path}")
    logger.info(f"Language     : {language}")
    logger.info(f"Output Chart : {chart_file}")
    logger.info("=" * 60)

    # 1. Instantiate the exact same service as BentoML
    service = WhisperXService()

    # 2. Run transcription with debug chart export
    audio_file = pathlib.Path(audio_path)
    result = service.transcribe(
        audio=audio_file,
        language=language,
        enable_diarization=enable_diarization,
        debug_chart_path=chart_file,
    )

    # 3. Save JSON Report
    json_file = out_dir / "debug_pipeline_report.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)

    logger.info("=" * 60)
    logger.info(f"DEBUG RUN FINISHED!")
    logger.info(f"Full Text: {result.full_text}")
    logger.info(f"Segments Count: {len(result.segments)}, Speakers: {result.speaker_count}")
    logger.info(f"Visual Chart Saved to: {chart_file}")
    logger.info(f"JSON Report Saved to  : {json_file}")
    logger.info("=" * 60)

    return result.model_dump()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debug WhisperX STT & Diarization Service")
    parser.add_argument("--audio", type=str, required=True, help="Path to input audio file (WAV/MP3)")
    parser.add_argument("--output-dir", type=str, default="./debug_output", help="Directory to save visual charts and reports")
    parser.add_argument("--lang", type=str, default="vi", help="Language code (default: vi)")
    parser.add_argument("--no-diarize", action="store_true", help="Disable speaker diarization")
    args = parser.parse_args()

    run_debug(
        audio_path=args.audio,
        output_dir=args.output_dir,
        language=args.lang,
        enable_diarization=not args.no_diarize,
    )
