"""Focused acquisition pipeline for videos consumed by the RAG module."""

from .domain import CrawlJobRequest, CrawledVideo, DiscoveryMethod, Platform

__all__ = ["CrawlJobRequest", "CrawledVideo", "DiscoveryMethod", "Platform"]
