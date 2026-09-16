"""PgVectorAdapter implementation for PostgreSQL with pgvector extension."""

import json
import math
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from module.video_rag.domain.entities.reference_pattern import SimilarVideoContext
from module.video_rag.port.vector_store_port import IVectorStorePort


class PgVectorAdapter(IVectorStorePort):
    """Adapter for PostgreSQL using the pgvector extension with asyncpg."""

    def __init__(
        self,
        engine: AsyncEngine,
        table_name: str = "viral_video_embeddings",
        dimension: int = 1024,
        fallback_mode: bool = True,
    ) -> None:
        self._engine = engine
        self._table_name = table_name
        self._dimension = dimension
        self._fallback_mode = fallback_mode
        self._sessionmaker = async_sessionmaker(bind=self._engine, class_=AsyncSession, expire_on_commit=False)
        self._table_initialized = False
        self._use_fallback = False
        self._memory_store: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
        """Calculate cosine similarity between two float vectors."""
        dot = sum(a * b for a, b in zip(v1, v2, strict=False))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return dot / (norm1 * norm2)

    async def initialize(self) -> None:
        """Create extension and table if they do not exist."""
        if self._table_initialized:
            return

        try:
            async with self._engine.begin() as conn:
                # Create extension
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                # Create table
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {self._table_name} (
                    id VARCHAR(64) PRIMARY KEY,
                    vector vector({self._dimension}),
                    metadata JSONB,
                    document TEXT
                );
                """
                await conn.execute(text(create_table_sql))
                # Create HNSW index for cosine distance
                create_index_sql = f"""
                CREATE INDEX IF NOT EXISTS {self._table_name}_hnsw_idx
                ON {self._table_name} USING hnsw (vector vector_cosine_ops);
                """
                await conn.execute(text(create_index_sql))

            self._table_initialized = True
        except Exception as exc:
            if self._fallback_mode:
                logger.warning(
                    f"PgVectorAdapter failed to initialize database ({exc}). Falling back to in-memory vector store."
                )
                self._use_fallback = True
                self._table_initialized = True
            else:
                raise

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
        """Insert or update a batch of vector records into pgvector."""
        if not ids:
            return

        await self.initialize()

        if self._use_fallback:
            for i in range(len(ids)):
                self._memory_store[ids[i]] = {
                    "id": ids[i],
                    "vector": vectors[i],
                    "metadata": metadatas[i],
                    "document": documents[i],
                }
            return

        async with self._sessionmaker() as session:
            for i in range(len(ids)):
                doc_id = ids[i]
                vec = vectors[i]
                meta = metadatas[i]
                doc = documents[i]

                # Convert vector to string representation [0.1, 0.2, ...]
                vec_str = "[" + ",".join(str(x) for x in vec) + "]"
                meta_json = json.dumps(meta, ensure_ascii=False)

                upsert_query = f"""
                INSERT INTO {self._table_name} (id, vector, metadata, document)
                VALUES (:id, CAST(:vec AS vector), CAST(:meta AS jsonb), :doc)
                ON CONFLICT (id) DO UPDATE SET
                    vector = EXCLUDED.vector,
                    metadata = EXCLUDED.metadata,
                    document = EXCLUDED.document;
                """
                await session.execute(
                    text(upsert_query),
                    {"id": doc_id, "vec": vec_str, "meta": meta_json, "doc": doc},
                )

            await session.commit()

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[SimilarVideoContext]:
        """Retrieve top-K nearest vectors using cosine similarity (1 - cosine distance)."""
        await self.initialize()

        if self._use_fallback:
            scored: list[tuple[float, dict[str, Any]]] = []
            for item in self._memory_store.values():
                sim = self._cosine_similarity(query_vector, item["vector"])
                scored.append((sim, item))
            scored.sort(key=lambda x: x[0], reverse=True)
            fallback_results: list[SimilarVideoContext] = []
            for sim, item in scored[:top_k]:
                fallback_results.append(
                    SimilarVideoContext(
                        id=item["id"],
                        document=item["document"],
                        metadata=item["metadata"],
                        score=round(float(sim), 4),
                    )
                )
            return fallback_results

        vec_str = "[" + ",".join(str(x) for x in query_vector) + "]"

        search_query = f"""
        SELECT id, document, metadata,
               1 - (vector <=> CAST(:vec AS vector)) AS similarity
        FROM {self._table_name}
        ORDER BY vector <=> CAST(:vec AS vector)
        LIMIT :top_k;
        """

        results: list[SimilarVideoContext] = []
        async with self._sessionmaker() as session:
            rows = await session.execute(
                text(search_query),
                {"vec": vec_str, "top_k": top_k},
            )
            for row in rows:
                doc_id = str(row[0])
                doc = str(row[1] or "")
                meta = row[2] if isinstance(row[2], dict) else json.loads(row[2] or "{}")
                similarity = round(float(row[3] or 0.0), 4)

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
        """Return total number of items in pgvector table."""
        await self.initialize()
        if self._use_fallback:
            return len(self._memory_store)

        count_query = f"SELECT COUNT(*) FROM {self._table_name};"
        async with self._sessionmaker() as session:
            result = await session.execute(text(count_query))
            return int(result.scalar_one_or_none() or 0)
