"""IThumbnailSelectorPort protocol."""

from typing import Protocol


class IThumbnailSelectorPort(Protocol):
    """Protocol for selecting the most engaging thumbnail from candidate frames."""

    async def select_best_frame(
        self,
        candidate_paths: list[str],
        video_context: str,
    ) -> str:
        """Rank candidate frames and select the most engaging one.

        Args:
            candidate_paths: List of file paths to candidate frame images.
            video_context: Transcript or summary context for semantic alignment.

        Returns:
            Path to the selected best frame.
        """
        ...
