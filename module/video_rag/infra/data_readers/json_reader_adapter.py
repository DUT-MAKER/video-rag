"""JsonDataReaderAdapter implementation."""

import json
from pathlib import Path
from typing import Any

from module.video_rag.domain.entities.video_record import RawVideoRecord
from module.video_rag.domain.exceptions import VideoRecordParsingError
from module.video_rag.port.data_reader_port import IDataReaderPort


class JsonDataReaderAdapter(IDataReaderPort):
    """Adapter for reading and normalizing video records from JSON sources."""

    def read_from_file(self, file_path: str) -> list[RawVideoRecord]:
        """Read video records list from a JSON file path."""
        path = Path(file_path)
        if not path.exists():
            raise VideoRecordParsingError(f"Data file not found at path: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise VideoRecordParsingError(f"Syntax error reading JSON file: {e}") from e

        if not isinstance(data, list):
            raise VideoRecordParsingError("Video knowledge data in JSON file must be a list/array.")

        return self.read_from_records(data)

    def read_from_json_string(self, json_content: str) -> list[RawVideoRecord]:
        """Read video records list from a raw JSON string."""
        try:
            data = json.loads(json_content)
        except Exception as e:
            raise VideoRecordParsingError(f"Invalid JSON string format: {e}") from e

        if not isinstance(data, list):
            raise VideoRecordParsingError("JSON content must be a list/array.")

        return self.read_from_records(data)

    async def read_records(self, file_path_or_url: str) -> list[RawVideoRecord]:
        """Async implementation of IDataReaderPort interface."""
        return self.read_from_file(file_path_or_url)

    def read_from_records(self, records: list[dict[str, Any]]) -> list[RawVideoRecord]:
        """Normalize raw dictionary records into RawVideoRecord domain entities."""
        result: list[RawVideoRecord] = []

        for item in records:
            if not isinstance(item, dict):
                continue

            caption = str(item.get("caption") or "").strip()

            raw_hashtag = item.get("hashtag") or ""
            if isinstance(raw_hashtag, list):
                hashtag = " ".join(str(h) for h in raw_hashtag).strip()
            else:
                hashtag = str(raw_hashtag).strip()

            transcript = str(item.get("transcript") or "").strip()
            image_url = str(item.get("image_url") or "").strip()
            summary = str(item.get("summary") or "").strip()
            video_url = str(item.get("video_url") or "").strip()

            if not caption and not transcript:
                continue

            record = RawVideoRecord(
                caption=caption,
                hashtag=hashtag,
                transcript=transcript,
                image_url=image_url,
                summary=summary,
                video_url=video_url,
            )
            result.append(record)

        return result
