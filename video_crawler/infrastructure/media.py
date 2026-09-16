"""Media acquisition through yt-dlp with no access-control bypass behavior."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import httpx
import yt_dlp

from video_crawler.config import CrawlerSettings
from video_crawler.domain import DiscoveredVideo, MediaArtifact


class YtDlpMediaResolver:
    def __init__(self, settings: CrawlerSettings) -> None:
        self.settings = settings

    async def resolve(self, video: DiscoveredVideo) -> MediaArtifact:
        self.settings.work_dir.mkdir(parents=True, exist_ok=True)
        work_dir = Path(tempfile.mkdtemp(prefix=f"{video.platform.value}-", dir=self.settings.work_dir))
        try:
            cookie_file = self._cookie_file(video, work_dir)
            info = await asyncio.to_thread(self._download, video.canonical_url, work_dir, cookie_file)
            video_path = self._video_path(info, work_dir)
            thumbnail_path = await self._thumbnail(video.thumbnail_url, work_dir)
            if thumbnail_path is None:
                thumbnail_path = await asyncio.to_thread(self._extract_frame, video_path, work_dir)
            return MediaArtifact(
                video_path=str(video_path),
                thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
                duration_seconds=float(info["duration"]) if info.get("duration") else None,
                work_dir=str(work_dir),
                metrics=self._metrics(info),
            )
        except Exception:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise

    async def cleanup(self, artifact: MediaArtifact) -> None:
        await asyncio.to_thread(shutil.rmtree, artifact.work_dir, True)

    def _download(self, url: str, work_dir: Path, cookie_file: Path | None) -> dict[str, Any]:
        options: dict[str, Any] = {
            "outtmpl": str(work_dir / "video.%(ext)s"),
            "format": "bv*+ba/b",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }
        if cookie_file:
            options["cookiefile"] = str(cookie_file)
        with yt_dlp.YoutubeDL(options) as downloader:
            return downloader.extract_info(url, download=True)

    def _cookie_file(self, video: DiscoveredVideo, work_dir: Path) -> Path | None:
        state_path = self.settings.session_file(video.platform.value)
        if not state_path.exists():
            return None
        state = json.loads(state_path.read_text(encoding="utf-8"))
        target = work_dir / "cookies.txt"
        lines = ["# Netscape HTTP Cookie File"]
        for cookie in state.get("cookies", []):
            domain = str(cookie.get("domain") or "")
            if not domain:
                continue
            include_subdomains = "TRUE" if domain.startswith(".") else "FALSE"
            secure = "TRUE" if cookie.get("secure") else "FALSE"
            expires = int(cookie.get("expires") or 0)
            lines.append(
                "\t".join(
                    [
                        domain,
                        include_subdomains,
                        str(cookie.get("path") or "/"),
                        secure,
                        str(expires),
                        str(cookie.get("name") or ""),
                        str(cookie.get("value") or ""),
                    ]
                )
            )
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        target.chmod(0o600)
        return target

    @staticmethod
    def _video_path(info: dict[str, Any], work_dir: Path) -> Path:
        requested = info.get("requested_downloads") or []
        generated = [
            path
            for path in work_dir.glob("video.*")
            if path.stem == "video"
            and path.suffix.lower() not in {".vtt", ".part", ".txt"}
        ]
        candidates = generated
        candidates.extend(
            Path(item["filepath"]) for item in requested if item.get("filepath")
        )
        for path in candidates:
            if path.exists() and path.suffix.lower() not in {".vtt", ".part", ".txt"}:
                return path
        raise RuntimeError("MEDIA_DOWNLOAD_FAILED: video file was not produced")

    @staticmethod
    def _metrics(info: dict[str, Any]) -> dict[str, int | float]:
        metrics: dict[str, int | float] = {}
        fields = {
            "view_count": "view_count",
            "like_count": "like_count",
            "comment_count": "comment_count",
            "share_count": "share_count",
            "repost_count": "share_count",
        }
        for source, target in fields.items():
            value = info.get(source)
            if target not in metrics and isinstance(value, (int, float)) and not isinstance(value, bool):
                metrics[target] = value
        return metrics

    @staticmethod
    async def _thumbnail(url: str, work_dir: Path) -> Path | None:
        if not url:
            return None
        if url.startswith("//"):
            url = f"https:{url}"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError:
            return None
        suffix = ".png" if "png" in response.headers.get("content-type", "") else ".jpg"
        path = work_dir / f"thumbnail{suffix}"
        path.write_bytes(response.content)
        return path

    @staticmethod
    def _extract_frame(video_path: Path, work_dir: Path) -> Path:
        output = work_dir / "thumbnail.jpg"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", "00:00:01", "-i", str(video_path), "-frames:v", "1", str(output)],
            check=True,
            capture_output=True,
        )
        return output
