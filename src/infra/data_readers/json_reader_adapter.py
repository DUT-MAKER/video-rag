"""JsonDataReaderAdapter implementation."""

import json
from pathlib import Path
from typing import Any

from src.core.domain.entities.video_record import RawVideoRecord
from src.core.domain.exceptions import VideoRecordParsingError
from src.core.ports.data_reader_port import IDataReaderPort


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

    def read_from_records(self, records: list[dict[str, Any]]) -> list[RawVideoRecord]:
        """Normalize raw dictionary records into RawVideoRecord domain entities.
        Supports both standard English keys and dataset-specific Vietnamese contract keys.
        """
        result: list[RawVideoRecord] = []

        for item in records:
            if not isinstance(item, dict):
                continue

            caption = str(item.get("caption") or item.get("title") or item.get("tieu_de") or "").strip()

            # Handle hashtag which may be a string or a list of strings
            raw_hashtag = item.get("hashtag") or item.get("hastag") or item.get("tags") or ""
            if isinstance(raw_hashtag, list):
                hashtag = " ".join(str(h) for h in raw_hashtag).strip()
            else:
                hashtag = str(raw_hashtag).strip()

            # Note: Dataset contract has typo 'trancsript'
            transcript = str(item.get("transcript") or item.get("trancsript") or item.get("loi_thoai") or "").strip()

            image_url = str(
                item.get("image_url") or item.get("hình ảnh") or item.get("hinh_anh") or item.get("thumbnail") or ""
            ).strip()

            summary = str(
                item.get("summary") or item.get("nội dung tóm tắt") or item.get("noi_dung_tom_tat") or ""
            ).strip()

            video_url = str(item.get("video_url") or item.get("url_video") or item.get("link_video") or "").strip()

            # Must contain at least caption or transcript to be valid
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
