"""Multi-Platform CLI Entrypoint for Video Crawler."""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import List, Optional

from loguru import logger

from module.crawler.domain import IpBlockedStopSignal, PlatformType
from module.crawler.platforms.youtube_shorts import (
    YouTubeShortsExtractor,
    YouTubeShortsPipeline,
    YouTubeShortsTranscriptAdapter,
)
from module.crawler.port import IPlatformCrawlerPort
from module.crawler.shared import (
    JsonFileDedupStore,
    LLMSummaryAdapter,
    LocalStorageAdapter,
    MinioStorageAdapter,
)


def extract_id_from_url(url_or_id: str) -> str:
    """Extracts video ID from URL or returns stripped ID."""
    url_or_id = url_or_id.strip()
    match = re.search(r"(?:shorts/|v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url_or_id)
    if match:
        return match.group(1)
    if len(url_or_id) == 11 and re.match(r"^[a-zA-Z0-9_-]+$", url_or_id):
        return url_or_id
    return url_or_id


def build_pipeline(
    platform: PlatformType,
    storage_type: str = "local",
    dedup_path: str = "data/crawled_manifest.json",
    fallback_on_ip_block: bool = False,
) -> IPlatformCrawlerPort:
    # 1. Shared storage
    if storage_type == "minio":
        try:
            storage = MinioStorageAdapter()
        except Exception as e:
            logger.warning(f"MinIO storage unavailable ({e}). Falling back to LocalStorageAdapter.")
            storage = LocalStorageAdapter()
    else:
        storage = LocalStorageAdapter()

    # 2. Shared summary and dedup
    summarizer = LLMSummaryAdapter()
    dedup_store = JsonFileDedupStore(manifest_path=dedup_path)

    # 3. Platform-specific pipeline
    if platform == PlatformType.YOUTUBE_SHORTS:
        extractor = YouTubeShortsExtractor()
        transcriber = YouTubeShortsTranscriptAdapter(fallback_on_ip_block=fallback_on_ip_block)
        return YouTubeShortsPipeline(
            extractor=extractor,
            transcriber=transcriber,
            storage=storage,
            summarizer=summarizer,
            dedup_store=dedup_store,
        )
    else:
        raise NotImplementedError(
            f"Platform crawler '{platform.value}' is not yet implemented. "
            f"Add adapter in module/crawler/platforms/{platform.value}/"
        )


def main():
    parser = argparse.ArgumentParser(description="Multi-Platform Video Crawler for RAG Viral Video")
    parser.add_argument("target", nargs="?", help="Video ID or Video URL to crawl")
    parser.add_argument(
        "--platform",
        choices=[p.value for p in PlatformType],
        default=PlatformType.YOUTUBE_SHORTS.value,
        help="Target platform (default: youtube_shorts)",
    )
    parser.add_argument("--file", "-f", help="Path to text file containing list of video IDs/URLs (one per line)")
    parser.add_argument("--storage", choices=["local", "minio"], default="local", help="Storage backend (default: local)")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay in seconds between requests to avoid rate limits (default: 3.0)")
    parser.add_argument("--output-dir", default="data/ingest_queue", help="Directory where JSON records are saved")
    parser.add_argument("--manifest", default="data/crawled_manifest.json", help="Path to dedup manifest file")

    args = parser.parse_args()

    platform = PlatformType(args.platform)
    targets: List[str] = []

    if args.target:
        targets.append(extract_id_from_url(args.target))
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"Target list file not found: {args.file}")
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip()
                if clean_line and not clean_line.startswith("#"):
                    targets.append(extract_id_from_url(clean_line))
    else:
        parser.print_help()
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        f"Starting crawler for platform [{platform.value}]. "
        f"Targets: {len(targets)}, Storage: {args.storage}, Delay: {args.delay}s"
    )
    pipeline = build_pipeline(platform=platform, storage_type=args.storage, dedup_path=args.manifest)

    success_count = 0
    skipped_count = 0

    for i, vid in enumerate(targets):
        logger.info(f"[{i+1}/{len(targets)}] Processing video: {vid}")
        try:
            result = pipeline.process_video(vid)
            if result:
                out_path = output_dir / f"{vid}.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info(f"[{vid}] Ingestion payload saved to {out_path}")
                success_count += 1
            else:
                skipped_count += 1

        except IpBlockedStopSignal as e:
            logger.critical("\n" + "=" * 70)
            logger.critical(f"STOPPING JOB: {platform.value} has rate-limited your IP address!")
            logger.critical(f"Details: {e}")
            logger.critical("ACTIONS REQUIRED:")
            logger.critical("  1. Pause crawling for 15-30 minutes, OR")
            logger.critical("  2. Switch network / connect through rotating proxy or VPN.")
            logger.critical("=" * 70)
            sys.exit(2)

        except Exception as e:
            logger.error(f"[{vid}] Error processing video: {e}")
            skipped_count += 1

        if i < len(targets) - 1 and args.delay > 0:
            time.sleep(args.delay)

    logger.info(f"Batch completed. Successfully crawled: {success_count}, Skipped/Failed: {skipped_count}")


if __name__ == "__main__":
    main()
