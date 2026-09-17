"""Preflight checks for third-party distribution metadata used by Dishka."""

from importlib import metadata

_DISHKA_FEATURE_DISTRIBUTIONS = ("sqlalchemy",)


def validate_runtime_dependencies() -> None:
    """Fail fast when a dependency's installed metadata is incomplete.

    Dishka evaluates optional integrations while it is imported.  A partially
    installed ``*.dist-info`` directory can make ``importlib.metadata`` return
    ``version=None`` and cause Dishka to fail much deeper in its internals.
    Keep this check immediately before the Dishka import so the resulting error
    identifies the repair action and is independent of the selected provider.
    """

    for distribution_name in _DISHKA_FEATURE_DISTRIBUTIONS:
        try:
            distribution = metadata.distribution(distribution_name)
        except metadata.PackageNotFoundError as exc:
            raise RuntimeError(
                f"Required distribution metadata is missing for {distribution_name!r}. "
                "Repair the environment with `uv sync --reinstall-package "
                f"{distribution_name}`."
            ) from exc

        version = distribution.version
        if not isinstance(version, str) or not version.strip():
            location = getattr(distribution, "_path", "unknown location")
            raise RuntimeError(
                f"Installed distribution metadata for {distribution_name!r} is incomplete "
                f"(version={version!r}, location={location}). Remove the broken virtualenv "
                "or run `uv sync --reinstall-package "
                f"{distribution_name}` before starting the API."
            )
