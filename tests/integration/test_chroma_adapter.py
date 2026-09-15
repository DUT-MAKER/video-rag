"""Integration tests for ChromaVectorStoreAdapter."""

import shutil
import tempfile

import pytest

from src.infra.vector_store.chroma_adapter import ChromaVectorStoreAdapter


@pytest.fixture
def temp_chroma_adapter():
    """Create adapter instance using temporary storage directory."""
    temp_dir = tempfile.mkdtemp(prefix="chroma_test_")
    adapter = ChromaVectorStoreAdapter(
        persist_dir=temp_dir,
        collection_name="test_viral_patterns",
    )
    yield adapter
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_chroma_adapter_upsert_and_search(temp_chroma_adapter: ChromaVectorStoreAdapter) -> None:
    """Verify vector upsert and cosine similarity search on persistent ChromaDB."""
    # 1. Upsert batch of 2 vectors
    ids = ["v1", "v2"]
    vectors = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]
    metadatas = [
        {
            "caption": "Video on 2-minute rule",
            "video_url": "https://minio/v1.mp4",
            "hook_candidate": "90% of people fail",
        },
        {
            "caption": "Video on social media algorithm",
            "video_url": "https://minio/v2.mp4",
            "hook_candidate": "Stop posting spam videos",
        },
    ]
    documents = ["2-minute habit rule", "social media algorithm"]

    await temp_chroma_adapter.upsert_batch(
        ids=ids,
        vectors=vectors,
        metadatas=metadatas,
        documents=documents,
    )

    count = await temp_chroma_adapter.count()
    assert count == 2

    # 2. Query with vector closest to v1: [0.9, 0.1, 0.0]
    query_vec = [0.9, 0.1, 0.0]
    search_results = await temp_chroma_adapter.search(query_vector=query_vec, top_k=2)

    assert len(search_results) == 2
    # First result must be v1 due to higher similarity
    assert search_results[0].id == "v1"
    assert search_results[0].caption == "Video on 2-minute rule"
    assert search_results[0].score > 0.8
