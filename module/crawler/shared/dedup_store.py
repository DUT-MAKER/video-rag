"""DedupStore adapter implementing IDedupStorePort (shared across all platforms)."""

import json
from pathlib import Path
from typing import Set

from loguru import logger

from module.crawler.port import IDedupStorePort


class JsonFileDedupStore(IDedupStorePort):
    """File-based persistent deduplication store.
    
    IMPORTANT NOTICE:
    This implementation is designed ONLY for single-process batch runs or development.
    It rewrites the JSON manifest on each processed item and is NOT safe for concurrent
    multi-process workers (such as multi-worker Celery). For multi-worker deployments,
    replace this with a PostgreSQL or Redis implementation using atomic locks/transactions.
    """

    def __init__(self, manifest_path: str = "data/crawled_manifest.json"):
        self.manifest_path = Path(manifest_path).resolve()
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._processed_ids: Set[str] = set()
        self._load()

    def _load(self) -> None:
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._processed_ids = set(data)
                logger.info(f"Loaded {len(self._processed_ids)} processed video IDs from manifest.")
            except Exception as e:
                logger.error(f"Failed to load dedup manifest {self.manifest_path}: {e}")
                self._processed_ids = set()

    def is_processed(self, video_id: str) -> bool:
        return video_id in self._processed_ids

    def mark_processed(self, video_id: str) -> None:
        self._processed_ids.add(video_id)
        try:
            with open(self.manifest_path, "w", encoding="utf-8") as f:
                json.dump(sorted(list(self._processed_ids)), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist video {video_id} to manifest: {e}")
