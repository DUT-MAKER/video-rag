"""YouTube Shorts extractor implementing IVideoExtractorPort."""

import os
import re
from typing import Any, Optional

from loguru import logger
import yt_dlp

from module.crawler.domain import DownloadedMedia, PlatformType, VideoMetadata
from module.crawler.port import IVideoExtractorPort


class YouTubeShortsExtractor(IVideoExtractorPort):
    """Adapter for YouTube Shorts metadata inspection and downloading via yt-dlp."""

    def __init__(self, quiet: bool = True):
        self.quiet = quiet

    def fetch_metadata(self, video_id: str) -> Optional[VideoMetadata]:
        url = f"https://www.youtube.com/shorts/{video_id}"
        ydl_opts = {
            "skip_download": True,
            "quiet": self.quiet,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    logger.warning(f"[{video_id}] yt-dlp returned empty info dictionary.")
                    return None
        except Exception as e:
            logger.warning(f"[{video_id}] Failed to fetch metadata: {e}")
            return None

        duration = float(info.get("duration") or 0)
        width = int(info.get("width") or 0)
        height = int(info.get("height") or 0)

        # Early filter: duration <= 65s AND vertical aspect ratio (height > width > 0)
        is_shorts = (0 < duration <= 65) and (height > width > 0)

        title = str(info.get("title") or "").strip()
        description = str(info.get("description") or "").strip()
        caption = f"{title}\n{description}".strip()

        tags = info.get("tags") or []
        found_hashtags = re.findall(r"#(\w+)", caption)
        clean_tags = [t.lstrip("#") for t in tags if t]
        all_hashtags = sorted(list(set(clean_tags + found_hashtags)))

        return VideoMetadata(
            video_id=video_id,
            platform=PlatformType.YOUTUBE_SHORTS,
            title=title,
            description=description,
            caption=caption,
            hashtags=all_hashtags,
            duration=duration,
            width=width,
            height=height,
            view_count=int(info.get("view_count") or 0),
            like_count=int(info.get("like_count") or 0),
            comment_count=int(info.get("comment_count") or 0),
            upload_date=str(info.get("upload_date") or ""),
            is_shorts=is_shorts,
            raw_info=info,
        )

    def download_media(
        self,
        video_id: str,
        output_dir: str,
        cached_info: Optional[dict[str, Any]] = None,
    ) -> DownloadedMedia:
        url = f"https://www.youtube.com/shorts/{video_id}"
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": f"{output_dir}/{video_id}.%(ext)s",
            "writethumbnail": True,
            "quiet": self.quiet,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if cached_info:
                    try:
                        ydl.process_ie_result(cached_info, download=True)
                    except Exception as ie_err:
                        logger.warning(
                            f"[{video_id}] process_ie_result failed ({ie_err}), falling back to ydl.download()"
                        )
                        ydl.download([url])
                else:
                    ydl.download([url])
        except Exception as e:
            logger.error(f"[{video_id}] Media download failed: {e}")
            return DownloadedMedia(video_path=None, thumbnail_path=None)

        video_path = f"{output_dir}/{video_id}.mp4"
        thumbnail_path = None
        for ext in ["jpg", "webp", "png"]:
            candidate = f"{output_dir}/{video_id}.{ext}"
            if os.path.exists(candidate):
                thumbnail_path = candidate
                break

        return DownloadedMedia(
            video_path=video_path if os.path.exists(video_path) else None,
            thumbnail_path=thumbnail_path,
        )
