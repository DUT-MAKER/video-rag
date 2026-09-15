"""IDataReaderPort protocol."""

from typing import Any, Protocol

from src.core.domain.entities.video_record import RawVideoRecord


class IDataReaderPort(Protocol):
    """Protocol for reading and normalizing video records from JSON sources."""

    def read_from_file(self, file_path: str) -> list[RawVideoRecord]:
        """Read and parse video records from a JSON file path."""
        ...

    def read_from_json_string(self, json_content: str) -> list[RawVideoRecord]:
        """Read and parse video records from a raw JSON string."""
        ...

    def read_from_records(self, records: list[dict[str, Any]]) -> list[RawVideoRecord]:
        """Normalize raw dictionary records (e.g., from API payload) into domain entities."""
        ...
