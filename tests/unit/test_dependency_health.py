"""Tests for dependency metadata preflight validation."""

from types import SimpleNamespace

import pytest

from backend.di import dependency_health


def test_validate_runtime_dependencies_accepts_versioned_distribution(monkeypatch):
    monkeypatch.setattr(
        dependency_health.metadata,
        "distribution",
        lambda name: SimpleNamespace(version="2.0.54"),
    )

    dependency_health.validate_runtime_dependencies()


def test_validate_runtime_dependencies_rejects_missing_version(monkeypatch):
    monkeypatch.setattr(
        dependency_health.metadata,
        "distribution",
        lambda name: SimpleNamespace(version=None, _path="broken.dist-info"),
    )

    with pytest.raises(RuntimeError, match="sqlalchemy.*incomplete"):
        dependency_health.validate_runtime_dependencies()


def test_validate_runtime_dependencies_rejects_missing_distribution(monkeypatch):
    def missing_distribution(name):
        raise dependency_health.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(dependency_health.metadata, "distribution", missing_distribution)

    with pytest.raises(RuntimeError, match="metadata is missing"):
        dependency_health.validate_runtime_dependencies()
