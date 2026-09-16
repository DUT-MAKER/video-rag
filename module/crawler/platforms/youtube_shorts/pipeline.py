"""YouTube Shorts Pipeline Orchestrator."""

import os
from pathlib import Path
import tempfile
from typing import Any, Optional

from loguru import logger

from module.crawler.domain import IpBlockedStopSignal, LLMUnavailableError
from module.crawler.port import (
    IDedupStorePort,
    IPlatformCrawlerPort,
    IStoragePort,
    ISummaryPort,
    ITranscriptPort,
    IVideoExtractorPort,
)


class YouTubeShortsPipeline(IPlatformCrawlerPort):
    """Pipeline orchestrating YouTube Shorts extraction, transcription, and storage."""

    def __init__(
        self,
        extractor: IVideoExtractorPort,
        transcriber: ITranscriptPort,
        storage: IStoragePort,
        summarizer: ISummaryPort,
        dedup_store: IDedupStorePort,
    ):
        self.extractor = extractor
        self.transcriber = transcriber
        self.storage = storage
        self.summarizer = summarizer
        self.dedup_store = dedup_store

    def process_video(self, video_id: str) -> Optional[dict[str, Any]]:
        # 1. Dedup check
        if self.dedup_store.is_processed(video_id):
            logger.info(f"[{video_id}] Already processed according to dedup store. Skipping.")
            return None

        # 2. Early metadata inspection and Shorts filtering
        try:
            metadata = self.extractor.fetch_metadata(video_id)
        except Exception as e:
            logger.error(f"[{video_id}] Exception during fetch_metadata: {e}")
            return None

        if not metadata:
            logger.warning(f"[{video_id}] Metadata is unavailable.")
            return None

        if not metadata.is_shorts:
            logger.info(
                f"[{video_id}] Skipped: Not a vertical Short "
                f"(Duration: {metadata.duration}s, Resolution: {metadata.width}x{metadata.height})."
            )
            return None

        # 3. Temporary directory for automated local file cleanup
        with tempfile.TemporaryDirectory() as temp_dir:
            # 4. Download media
            try:
                media = self.extractor.download_media(
                    video_id, temp_dir, cached_info=metadata.raw_info
                )
            except Exception as e:
                logger.error(f"[{video_id}] Exception during download_media: {e}")
                return None

            if not media.video_path or not os.path.exists(media.video_path):
                logger.warning(f"[{video_id}] Video download failed or file missing.")
                return None

            # 5. Extract transcript with timestamps
            try:
                transcript_res = self.transcriber.extract_transcript(
                    video_id, media.video_path
                )
            except IpBlockedStopSignal:
                logger.critical(f"[{video_id}] Re-raising IpBlockedStopSignal to orchestrator caller.")
                raise
            except Exception as e:
                logger.error(f"[{video_id}] Unexpected error in transcription: {e}")
                transcript_res = None

            # 6. Upload assets to storage
            video_url = ""
            image_url = ""
            try:
                video_url = self.storage.upload_file(
                    media.video_path, f"videos/{video_id}.mp4"
                )
                if media.thumbnail_path and os.path.exists(media.thumbnail_path):
                    ext = Path(media.thumbnail_path).suffix
                    image_url = self.storage.upload_file(
                        media.thumbnail_path, f"thumbnails/{video_id}{ext}"
                    )
            except Exception as e:
                logger.error(f"[{video_id}] Storage upload failed: {e}")
                return None

            # 7. Summarize via LLM (No text fabrication)
            summary: Optional[str] = None
            full_transcript = transcript_res.full_text if transcript_res else ""
            try:
                summary = self.summarizer.summarize(metadata.caption, full_transcript)
            except LLMUnavailableError as e:
                logger.warning(f"[{video_id}] LLM summary unavailable: {e}. Setting summary to None.")
                summary = None
            except Exception as e:
                logger.error(f"[{video_id}] Unexpected error calling summarizer: {e}")
                summary = None

            # 8. Mark video as successfully processed in dedup store
            self.dedup_store.mark_processed(video_id)

            # 9. Format output dictionary complying with PRD Data Contract
            segments = transcript_res.segments if transcript_res else []
            is_auto = transcript_res.is_auto_generated if transcript_res else True

            return {
                "caption": metadata.caption,
                "hashtag": metadata.hashtags,
                "transcript": full_transcript,
                "image_url": image_url,
                "summary": summary,
                "video_url": video_url,
                "_enriched_metadata": {
                    "platform": metadata.platform.value if hasattr(metadata.platform, "value") else str(metadata.platform),
                    "video_id": metadata.video_id,
                    "duration": metadata.duration,
                    "aspect_ratio": f"{metadata.width}:{metadata.height}",
                    "upload_date": metadata.upload_date,
                    "is_auto_generated": is_auto,
                    "metrics": {
                        "view_count": metadata.view_count,
                        "like_count": metadata.like_count,
                        "comment_count": metadata.comment_count,
                    },
                    "transcript_segments": [
                        {"start": s.start, "end": s.end, "text": s.text}
                        for s in segments
                    ],
                },
            }
