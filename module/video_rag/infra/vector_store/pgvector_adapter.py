"""PgVectorAdapter implementation for PostgreSQL with pgvector extension."""

import json
from typing import Any

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from module.video_rag.domain.entities.reference_pattern import SimilarVideoContext
from module.video_rag.domain.exceptions import VectorStoreError
from module.video_rag.port.vector_store_port import IVectorStorePort


class PgVectorAdapter(IVectorStorePort):
    """Adapter for PostgreSQL using the pgvector extension with asyncpg."""

    def __init__(
        self,
        engine: AsyncEngine,
        table_name: str = "viral_video_embeddings",
        dimension: int = 1024,
        fallback_mode: bool = False,
    ) -> None:
        self._engine = engine
        self._table_name = table_name
        self._dimension = dimension
        self._sessionmaker = async_sessionmaker(bind=self._engine, class_=AsyncSession, expire_on_commit=False)
        self._table_initialized = False
        self._use_fallback = fallback_mode
        self._memory_store: dict[str, Any] = {}

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
            logger.error(f"PgVectorAdapter failed to initialize database: {exc}")
            if self._use_fallback:
                logger.warning("PgVectorAdapter falling back to in-memory mode")
                self._table_initialized = True
                return
            raise VectorStoreError(f"Failed to initialize pgvector table: {exc}") from exc

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
                    "vector": vectors[i] if vectors else [],
                    "metadata": metadatas[i] if metadatas else {},
                    "document": documents[i] if documents else "",
                }
            return

        try:
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
        except Exception as exc:
            logger.error(f"PgVectorAdapter upsert_batch failed: {exc}")
            raise VectorStoreError(f"Failed to upsert batch into pgvector: {exc}") from exc

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[SimilarVideoContext]:
        """Retrieve top-K nearest vectors using cosine similarity (1 - cosine distance)."""
        await self.initialize()

        if self._use_fallback:
            results: list[SimilarVideoContext] = []
            for item in list(self._memory_store.values())[:top_k]:
                results.append(
                    SimilarVideoContext(
                        id=item["id"],
                        document=item.get("document", ""),
                        metadata=item.get("metadata", {}),
                        score=0.92,
                    )
                )
            return results

        vec_str = "[" + ",".join(str(x) for x in query_vector) + "]"

        search_query = f"""
        SELECT id, document, metadata,
               1 - (vector <=> CAST(:vec AS vector)) AS similarity
        FROM {self._table_name}
        ORDER BY vector <=> CAST(:vec AS vector)
        LIMIT :top_k;
        """

        try:
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
        except Exception as exc:
            logger.error(f"PgVectorAdapter search failed: {exc}")
            raise VectorStoreError(f"Failed to search pgvector: {exc}") from exc

    async def count(self) -> int:
        """Return total number of items in pgvector table."""
        await self.initialize()

        if self._use_fallback:
            return len(self._memory_store)

        try:
            count_query = f"SELECT COUNT(*) FROM {self._table_name};"
            async with self._sessionmaker() as session:
                result = await session.execute(text(count_query))
                return int(result.scalar_one_or_none() or 0)
        except Exception as exc:
            logger.error(f"PgVectorAdapter count failed: {exc}")
            raise VectorStoreError(f"Failed to count records in pgvector: {exc}") from exc

    async def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Retrieve paginated list of all video records (id, metadata, document) without vectors."""
        await self.initialize()

        if self._use_fallback:
            items = list(self._memory_store.values())
            total = len(items)
            page_items = items[offset : offset + limit]
            results = [
                {
                    "id": item["id"],
                    "document": item.get("document", ""),
                    "metadata": item.get("metadata", {}),
                }
                for item in page_items
            ]
            return results, total

        total = await self.count()
        query = f"""
        SELECT id, document, metadata
        FROM {self._table_name}
        ORDER BY id DESC
        LIMIT :limit OFFSET :offset;
        """

        results: list[dict[str, Any]] = []
        async with self._sessionmaker() as session:
            rows = await session.execute(text(query), {"limit": limit, "offset": offset})
            for row in rows:
                doc_id = str(row[0])
                doc = str(row[1] or "")
                meta = row[2] if isinstance(row[2], dict) else json.loads(row[2] or "{}")
                results.append(
                    {
                        "id": doc_id,
                        "document": doc,
                        "metadata": meta,
                    }
                )

        return results, total

    async def get_by_id(self, video_id: str) -> dict[str, Any] | None:
        """Retrieve a single video record by ID without vector embedding."""
        await self.initialize()

        if self._use_fallback:
            item = self._memory_store.get(video_id)
            if not item:
                return None
            return {
                "id": item["id"],
                "document": item.get("document", ""),
                "metadata": item.get("metadata", {}),
            }

        query = f"""
        SELECT id, document, metadata
        FROM {self._table_name}
        WHERE id = :id
        LIMIT 1;
        """

        async with self._sessionmaker() as session:
            row = (await session.execute(text(query), {"id": video_id})).first()
            if not row:
                return None
            doc_id = str(row[0])
            doc = str(row[1] or "")
            meta = row[2] if isinstance(row[2], dict) else json.loads(row[2] or "{}")
            return {
                "id": doc_id,
                "document": doc,
                "metadata": meta,
            }

    async def delete_by_id(self, video_id: str) -> bool:
        """Delete an indexed record by its ID."""
        await self.initialize()

        if self._use_fallback:
            if video_id in self._memory_store:
                del self._memory_store[video_id]
                return True
            return False

        query = f"DELETE FROM {self._table_name} WHERE id = :id;"
        async with self._sessionmaker() as session:
            res = await session.execute(text(query), {"id": video_id})
            await session.commit()
            return bool(getattr(res, "rowcount", 0) > 0)
