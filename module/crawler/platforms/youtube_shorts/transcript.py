"""YouTube Shorts subtitle adapter implementing ITranscriptPort."""

from typing import Optional

from loguru import logger
from youtube_transcript_api import (
    NoTranscriptFound,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
    YouTubeTranscriptApiException,
)
from youtube_transcript_api._errors import IpBlocked

from module.crawler.domain import (
    IpBlockedStopSignal,
    TranscriptResult,
    TranscriptSegment,
)
from module.crawler.port import ITranscriptPort
from module.crawler.shared.whisper_asr import WhisperASREngine


class YouTubeShortsTranscriptAdapter(ITranscriptPort):
    """Hybrid subtitle adapter specifically for YouTube:
    
    Tier 1: youtube-transcript-api==1.2.4 (Manual subtitles first, then Auto ASR).
    Circuit Breaker: Raises IpBlockedStopSignal when rate-limited.
    Tier 2: Shared WhisperASREngine fallback when subtitles are unavailable.
    """

    def __init__(self, whisper_model_size: str = "base", fallback_on_ip_block: bool = False):
        self._api = YouTubeTranscriptApi()
        self.whisper_engine = WhisperASREngine(model_size=whisper_model_size)
        self.fallback_on_ip_block = fallback_on_ip_block

    def extract_transcript(
        self,
        video_id: str,
        local_media_path: Optional[str] = None,
    ) -> TranscriptResult:
        # Tier 1: Try YouTube timedtext API
        try:
            transcript_list = self._api.list(video_id)
            try:
                # 1a. Prioritize manually created subtitles
                selected_transcript = transcript_list.find_manually_created_transcript(["vi", "en"])
                is_auto_generated = False
                logger.info(f"[{video_id}] Found manual transcript ({selected_transcript.language_code}).")
            except NoTranscriptFound:
                # 1b. Fallback to auto-generated ASR captions
                selected_transcript = transcript_list.find_generated_transcript(["vi", "en"])
                is_auto_generated = True
                logger.info(f"[{video_id}] Found auto-generated transcript ({selected_transcript.language_code}).")

            fetched = selected_transcript.fetch()
            raw_data = fetched.to_raw_data()

            segments = [
                TranscriptSegment(
                    start=round(float(item["start"]), 2),
                    end=round(float(item["start"]) + float(item["duration"]), 2),
                    text=str(item["text"]).strip(),
                )
                for item in raw_data
                if str(item.get("text", "")).strip()
            ]
            full_text = " ".join(s.text for s in segments)
            return TranscriptResult(
                full_text=full_text,
                segments=segments,
                is_auto_generated=is_auto_generated,
            )

        except IpBlocked as e:
            if self.fallback_on_ip_block:
                logger.warning(
                    f"[{video_id}] YouTube timedtext rate-limited IP. Falling back to local Whisper ASR as requested."
                )
                if local_media_path:
                    return self.whisper_engine.transcribe(local_media_path, video_id=video_id)
                return TranscriptResult(full_text="", segments=[], is_auto_generated=True)

            # STOP SIGNAL: Halt job to protect compute unless explicit fallback requested
            logger.critical(
                f"[IP BLOCKED STOP SIGNAL] YouTube has blocked IP on timedtext for video {video_id}: {e}"
            )
            raise IpBlockedStopSignal(
                f"YouTube timedtext rate-limit triggered on video {video_id}. Pipeline must halt."
            ) from e

        except (NoTranscriptFound, TranscriptsDisabled) as e:
            logger.info(
                f"[{video_id}] No online subtitles ({type(e).__name__}). Falling back to Whisper ASR."
            )

        except YouTubeTranscriptApiException as e:
            logger.warning(
                f"[{video_id}] YouTubeTranscriptApi error ({type(e).__name__}: {e}). Falling back to Whisper."
            )

        except Exception as e:
            logger.warning(
                f"[{video_id}] Unexpected error in transcript extraction ({type(e).__name__}: {e}). Falling back to Whisper."
            )

        # Tier 2: Delegate to shared Faster-Whisper ASR engine
        if local_media_path:
            return self.whisper_engine.transcribe(local_media_path, video_id=video_id)
        return TranscriptResult(full_text="", segments=[], is_auto_generated=True)
