"""ChromaVectorStoreAdapter implementation."""

from pathlib import Path
from typing import Any

import chromadb

from module.video_rag.domain.entities.reference_pattern import SimilarVideoContext
from module.video_rag.port.vector_store_port import IVectorStorePort


class ChromaVectorStoreAdapter(IVectorStorePort):
    """Adapter for vector storage and cosine similarity search using ChromaDB Persistent."""

    def __init__(
        self,
        persist_dir: str = "./data/storage/chroma",
        collection_name: str = "viral_video_patterns",
    ) -> None:
        self._persist_dir = persist_dir
        self._collection_name = collection_name

        # Ensure target storage directory exists
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        # Initialize Chroma persistent client
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    async def upsert(
        self,
        id: str,
        vector: list[float],
        metadata: dict[str, Any],
        document: str,
    ) -> None:
        """Insert or update a single vector record."""
        await self.upsert_batch(
            ids=[id],
            vectors=[vector],
            metadatas=[metadata],
            documents=[document],
        )

    async def upsert_batch(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict[str, Any]],
        documents: list[str],
    ) -> None:
        """Insert or update a batch of vector records."""
        if not ids:
            return

        # ChromaDB requires metadata values to be primitive types: int, float, str, or bool
        cleaned_metadatas = []
        for meta in metadatas:
            cleaned = {}
            for k, v in meta.items():
                if isinstance(v, (int, float, str, bool)):
                    cleaned[k] = v
                elif v is None:
                    cleaned[k] = ""
                else:
                    cleaned[k] = str(v)
            cleaned_metadatas.append(cleaned)

        self._collection.upsert(
            ids=ids,
            embeddings=vectors,
            metadatas=cleaned_metadatas,
            documents=documents,
        )

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[SimilarVideoContext]:
        """Retrieve top-K nearest vectors by cosine distance."""
        current_count = self._collection.count()
        if current_count == 0:
            return []

        actual_k = min(top_k, current_count)
        query_results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=actual_k,
            include=["documents", "metadatas", "distances"],
        )

        results: list[SimilarVideoContext] = []
        ids = query_results.get("ids", [[]])[0]
        documents = query_results.get("documents", [[]])[0]
        metadatas = query_results.get("metadatas", [[]])[0]
        distances = query_results.get("distances", [[]])[0]

        for i in range(len(ids)):
            doc_id = ids[i]
            doc = documents[i] if i < len(documents) else ""
            meta = metadatas[i] if i < len(metadatas) else {}
            dist = distances[i] if i < len(distances) else 1.0

            # Cosine similarity score = 1.0 - distance
            similarity = round(max(0.0, min(1.0, 1.0 - float(dist))), 4)

            results.append(
                SimilarVideoContext(
                    id=doc_id,
                    document=doc,
                    metadata=meta,
                    score=similarity,
                )
            )

        return results

    async def count(self) -> int:
        """Return total number of items in collection."""
        return int(self._collection.count())
