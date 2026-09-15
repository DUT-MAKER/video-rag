"""IDataReaderPort protocol."""

from typing import Protocol

from module.video_rag.domain.entities.video_record import RawVideoRecord


class IDataReaderPort(Protocol):
    """Protocol for reading raw viral video dataset from storage or JSON files."""

    async def read_records(self, file_path_or_url: str) -> list[RawVideoRecord]:
        """Load and parse dataset into domain RawVideoRecord entities."""
        ...
