"""IngestVideoDataUseCase implementation."""

from dataclasses import dataclass
from typing import Any

from src.core.domain.exceptions import VideoRecordParsingError
from src.core.ports.data_reader_port import IDataReaderPort
from src.core.ports.embedding_port import IEmbeddingPort
from src.core.ports.vector_store_port import IVectorStorePort


@dataclass
class IngestionResult:
    """Summary of data ingestion operation."""

    total_processed: int
    total_indexed: int
    extracted_hooks: list[str]
    indexed_ids: list[str]


class IngestVideoDataUseCase:
    """Coordinates reading, processing, embedding, and indexing of viral video records."""

    def __init__(
        self,
        data_reader: IDataReaderPort,
        embedding_port: IEmbeddingPort,
        vector_store_port: IVectorStorePort,
    ) -> None:
        self._reader = data_reader
        self._embed = embedding_port
        self._vector_store = vector_store_port

    async def execute(self, source: str | list[dict[str, Any]]) -> IngestionResult:
        """Execute ingestion from a file path or raw dictionary list."""
        if isinstance(source, str):
            records = self._reader.read_from_file(source)
        elif isinstance(source, list):
            records = self._reader.read_from_records(source)
        else:
            raise VideoRecordParsingError(f"Invalid data source type: {type(source)}")

        if not records:
            return IngestionResult(
                total_processed=0,
                total_indexed=0,
                extracted_hooks=[],
                indexed_ids=[],
            )

        # 1. Extract searchable text representations, IDs, and metadata
        texts_to_embed = [record.to_searchable_text() for record in records]
        ids = [record.id for record in records]
        metadatas = [record.to_metadata() for record in records]
        extracted_hooks = [record.extract_hook() for record in records]

        # 2. Batch vector embedding
        vectors = await self._embed.embed_batch(texts_to_embed)

        # 3. Upsert into Vector Store
        await self._vector_store.upsert_batch(
            ids=ids,
            vectors=vectors,
            metadatas=metadatas,
            documents=texts_to_embed,
        )

        return IngestionResult(
            total_processed=len(records),
            total_indexed=len(ids),
            extracted_hooks=extracted_hooks,
            indexed_ids=ids,
        )
