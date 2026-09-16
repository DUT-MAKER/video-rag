"""Shared crawler components reusable across platforms."""

from module.crawler.shared.dedup_store import JsonFileDedupStore
from module.crawler.shared.llm_summary import LLMSummaryAdapter
from module.crawler.shared.storage import LocalStorageAdapter, MinioStorageAdapter
from module.crawler.shared.whisper_asr import WhisperASREngine

__all__ = [
    "MinioStorageAdapter",
    "LocalStorageAdapter",
    "LLMSummaryAdapter",
    "JsonFileDedupStore",
    "WhisperASREngine",
]
