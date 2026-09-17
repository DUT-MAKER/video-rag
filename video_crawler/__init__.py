"""Focused acquisition pipeline for videos stored in S3/MinIO."""

from .domain import CrawlJobRequest, CrawledVideo, DiscoveryMethod, Platform

__all__ = ["CrawlJobRequest", "CrawledVideo", "DiscoveryMethod", "Platform"]
