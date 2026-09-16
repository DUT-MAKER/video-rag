from pathlib import Path

import httpx
import pytest

from video_crawler.config import CrawlerSettings
from video_crawler.domain import MediaArtifact
from video_crawler.infrastructure.media import YtDlpMediaResolver
from video_crawler.infrastructure.summarizer import (
    ExtractiveSummaryProvider,
    LlmSummaryProvider,
)
from video_crawler.infrastructure.transcript import SubtitleWhisperTranscriptProvider


def test_vtt_reader_removes_timestamps_markup_and_duplicates(tmp_path: Path) -> None:
    subtitle = tmp_path / "subtitle.vtt"
    subtitle.write_text(
        "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\n<c>First line</c>\n"
        "00:00:02.000 --> 00:00:04.000\nFirst line\nSecond line\n",
        encoding="utf-8",
    )
    assert SubtitleWhisperTranscriptProvider._read_vtt(subtitle) == "First line Second line"


@pytest.mark.asyncio
async def test_transcript_falls_back_to_asr_when_subtitle_is_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    subtitle = tmp_path / "empty.vtt"
    subtitle.write_text("WEBVTT\n", encoding="utf-8")
    provider = SubtitleWhisperTranscriptProvider(CrawlerSettings())
    monkeypatch.setattr(provider, "_whisper", lambda _: "Transcript from ASR")
    artifact = MediaArtifact("video.mp4", None, [str(subtitle)], 10.0, str(tmp_path))

    assert await provider.transcribe(artifact) == "Transcript from ASR"


def test_thumbnail_falls_back_to_ffmpeg_frame(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> None:
        calls.append(command)

    monkeypatch.setattr("video_crawler.infrastructure.media.subprocess.run", fake_run)
    output = YtDlpMediaResolver._extract_frame(tmp_path / "video.mp4", tmp_path)

    assert output == tmp_path / "thumbnail.jpg"
    assert calls[0][0] == "ffmpeg"


@pytest.mark.asyncio
async def test_extractive_summary_uses_caption_and_first_sentences() -> None:
    summary = await ExtractiveSummaryProvider().summarize(
        "Retention lesson",
        "Start with a promise. Show proof immediately. This third sentence is not needed.",
    )
    assert summary == "Retention lesson. Start with a promise. Show proof immediately."


@pytest.mark.asyncio
async def test_llm_summary_returns_generated_text(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = LlmSummaryProvider()

    async def fake_generate(caption: str, transcript: str) -> str:
        assert caption == "Retention lesson"
        assert transcript == "Full transcript"
        return "A concise generated summary."

    monkeypatch.setattr(provider, "_generate", fake_generate)

    assert await provider.summarize("Retention lesson", "Full transcript") == (
        "A concise generated summary."
    )


@pytest.mark.asyncio
async def test_llm_summary_falls_back_without_failing_video(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = LlmSummaryProvider()

    async def unavailable(caption: str, transcript: str) -> str:
        raise httpx.ConnectError("summary API unavailable")

    monkeypatch.setattr(provider, "_generate", unavailable)

    summary = await provider.summarize(
        "Retention lesson",
        "Start with a promise. Show proof immediately. This sentence is omitted.",
    )
    assert summary == "Retention lesson. Start with a promise. Show proof immediately."
