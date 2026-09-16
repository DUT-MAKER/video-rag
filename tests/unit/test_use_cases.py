"""Unit tests for Core Use Cases with Fake Ports."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from module.video_rag.domain.entities.extraction_result import VideoExtractionResult
from module.video_rag.domain.entities.reference_pattern import SimilarVideoContext
from module.video_rag.domain.entities.video_record import RawVideoRecord
from module.video_rag.domain.entities.viral_script import CallToAction, Hook, Scene, ViralScript
from module.video_rag.domain.exceptions import DomainValidationError
from module.video_rag.domain.value_objects.hook_type import HookType
from module.video_rag.domain.value_objects.platform_target import PlatformTarget
from module.video_rag.port.data_reader_port import IDataReaderPort
from module.video_rag.port.embedding_port import IEmbeddingPort
from module.video_rag.port.llm_port import ILLMPort
from module.video_rag.port.rerank_port import IRerankPort, RerankedDocument
from module.video_rag.port.vector_store_port import IVectorStorePort
from module.video_rag.service.video_extraction_service import VideoExtractionPipelineService
from module.video_rag.use_case.generate_viral_script import GenerateViralScriptUseCase
from module.video_rag.use_case.ingest_video_data import IngestVideoDataUseCase, VideoItemInput
from module.video_rag.use_case.search_viral_patterns import SearchViralPatternsUseCase


class FakeDataReader(IDataReaderPort):
    def __init__(self, sample_records: list[RawVideoRecord] | None = None) -> None:
        self.records = sample_records or []

    def read_from_file(self, file_path: str) -> list[RawVideoRecord]:
        return self.records

    def read_from_json_string(self, json_content: str) -> list[RawVideoRecord]:
        return self.records

    def read_from_records(self, records: list[dict[str, Any]]) -> list[RawVideoRecord]:
        return self.records


class FakeEmbeddingPort(IEmbeddingPort):
    async def embed_text(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]

    async def get_embedding(self, text: str) -> list[float]:
        return await self.embed_text(text)

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        return await self.embed_batch(texts)


class FakeVectorStorePort(IVectorStorePort):
    def __init__(self) -> None:
        self.storage: list[dict[str, Any]] = []

    async def upsert(self, id: str, vector: list[float], metadata: dict[str, Any], document: str) -> None:
        self.storage.append({"id": id, "vector": vector, "metadata": metadata, "document": document})

    async def upsert_batch(
        self, ids: list[str], vectors: list[list[float]], metadatas: list[dict[str, Any]], documents: list[str]
    ) -> None:
        for i in range(len(ids)):
            self.storage.append(
                {
                    "id": ids[i],
                    "vector": vectors[i],
                    "metadata": metadatas[i],
                    "document": documents[i],
                }
            )

    async def search(self, query_vector: list[float], top_k: int = 5) -> list[SimilarVideoContext]:
        results = []
        for item in self.storage[:top_k]:
            results.append(
                SimilarVideoContext(
                    id=item["id"],
                    document=item["document"],
                    metadata=item["metadata"],
                    score=0.95,
                )
            )
        return results

    async def count(self) -> int:
        return len(self.storage)


class FakeLLMPort(ILLMPort):
    async def generate_script(
        self,
        topic: str,
        target_audience: str,
        duration_seconds: int,
        platform: PlatformTarget,
        hook_style: str | None,
        reference_contexts: list[SimilarVideoContext],
    ) -> ViralScript:
        return ViralScript(
            title=f"Viral Video: {topic}",
            target_niche=target_audience,
            platform=platform,
            target_duration_seconds=duration_seconds,
            hook=Hook(
                hook_type=HookType.PROBLEM_AGITATE,
                script="Test hook statement",
                visual_action="Camera zoom",
                retention_rationale="Retains audience",
                duration_seconds=4,
            ),
            scenes=[
                Scene(
                    scene_number=1,
                    time_range="00:00 - 00:04",
                    narration="Test narration",
                    visual_action="Test visual",
                    image_prompt="Test image prompt",
                    video_prompt="Test video prompt",
                    audio_sfx_cue="Test sfx",
                )
            ],
            call_to_action=CallToAction(script="Follow me!", visual_cue="Follow icon"),
            references=[],
            suggested_hashtags=["#test", f"#{platform.value}"],
        )


class FakeRerankPort(IRerankPort):
    def __init__(self, reversed_order: bool = False) -> None:
        self.reversed_order = reversed_order

    async def rerank(self, query: str, documents: list[str], top_n: int = 3) -> list[RerankedDocument]:
        indices = list(range(len(documents)))
        if self.reversed_order:
            indices = list(reversed(indices))
        return [
            RerankedDocument(index=idx, score=0.99 - (i * 0.1), text=documents[idx])
            for i, idx in enumerate(indices[:top_n])
        ]


@pytest.mark.asyncio
async def test_ingest_video_data_use_case() -> None:
    fake_embed = FakeEmbeddingPort()
    fake_vector = FakeVectorStorePort()
    mock_extract = AsyncMock(spec=VideoExtractionPipelineService)
    mock_extract.execute.return_value = VideoExtractionResult(
        video_path="/tmp/video.mp4",
        transcript="Never give up on daily momentum.",
        transcript_with_speakers="SPEAKER_00 [0.0s -> 5.0s]: Never give up on daily momentum.",
        speaker_count=1,
        thumbnail_path="/tmp/thumb.jpg",
        caption="2-Minute Rule",
        summary="Summary",
        hashtag="#viral",
    )

    use_case = IngestVideoDataUseCase(
        embedding_port=fake_embed,
        vector_store_port=fake_vector,
        extract_service=mock_extract,
    )

    result = await use_case.execute(
        VideoItemInput(video_path="/tmp/video.mp4", caption="2-Minute Rule", hashtag="#viral")
    )
    assert result.total_processed == 1
    assert result.total_indexed == 1
    assert len(fake_vector.storage) == 1
    assert fake_vector.storage[0]["metadata"]["caption"] == "2-Minute Rule"


@pytest.mark.asyncio
async def test_search_viral_patterns_use_case() -> None:
    fake_embed = FakeEmbeddingPort()
    fake_vector = FakeVectorStorePort()
    await fake_vector.upsert(
        id="v1",
        vector=[0.1, 0.2, 0.3],
        metadata={"caption": "Benchmark Video 1", "hook_candidate": "Hook 1"},
        document="Content 1",
    )

    use_case = SearchViralPatternsUseCase(
        embedding_port=fake_embed,
        vector_store_port=fake_vector,
    )

    results = await use_case.execute(query="habit", top_k=5)
    assert len(results) == 1
    assert results[0].caption == "Benchmark Video 1"
    assert results[0].hook_candidate == "Hook 1"


@pytest.mark.asyncio
async def test_generate_viral_script_use_case() -> None:
    fake_llm = FakeLLMPort()
    fake_embed = FakeEmbeddingPort()
    fake_vector = FakeVectorStorePort()
    await fake_vector.upsert(
        id="v1",
        vector=[0.1, 0.2, 0.3],
        metadata={
            "caption": "Benchmark Discipline Video",
            "hook_candidate": "Stop scrolling if you...",
            "video_url": "https://minio/sample.mp4",
        },
        document="Discipline doc",
    )

    use_case = GenerateViralScriptUseCase(
        llm_port=fake_llm,
        embedding_port=fake_embed,
        vector_store_port=fake_vector,
    )

    script = await use_case.execute(
        topic="How to wake up early without feeling tired",
        target_audience="Young Professionals",
        duration_seconds=45,
        platform=PlatformTarget.TIKTOK,
    )

    assert "How to wake up early" in script.title
    assert script.platform == PlatformTarget.TIKTOK
    assert len(script.references) == 1
    assert script.references[0].original_caption == "Benchmark Discipline Video"


@pytest.mark.asyncio
async def test_generate_viral_script_validation() -> None:
    fake_llm = FakeLLMPort()
    fake_embed = FakeEmbeddingPort()
    fake_vector = FakeVectorStorePort()

    use_case = GenerateViralScriptUseCase(
        llm_port=fake_llm,
        embedding_port=fake_embed,
        vector_store_port=fake_vector,
    )

    with pytest.raises(DomainValidationError):
        await use_case.execute(topic="")

    with pytest.raises(DomainValidationError):
        await use_case.execute(topic="Valid Topic", duration_seconds=5)


@pytest.mark.asyncio
async def test_generate_viral_script_with_reranking() -> None:
    fake_llm = FakeLLMPort()
    fake_embed = FakeEmbeddingPort()
    fake_vector = FakeVectorStorePort()
    # FakeRerankPort with reversed_order will reverse candidate order
    fake_rerank = FakeRerankPort(reversed_order=True)

    await fake_vector.upsert(
        id="cand_1",
        vector=[0.1, 0.2, 0.3],
        metadata={"caption": "Video 1", "hook_candidate": "Hook 1"},
        document="Document 1",
    )
    await fake_vector.upsert(
        id="cand_2",
        vector=[0.1, 0.2, 0.3],
        metadata={"caption": "Video 2", "hook_candidate": "Hook 2"},
        document="Document 2",
    )

    use_case = GenerateViralScriptUseCase(
        llm_port=fake_llm,
        embedding_port=fake_embed,
        vector_store_port=fake_vector,
        rerank_port=fake_rerank,
        candidate_k=10,
    )

    script = await use_case.execute(
        topic="Morning routine",
        target_audience="General",
        top_k_patterns=2,
    )

    # Because rerank reversed the order, Video 2 should now be first!
    assert len(script.references) == 2
    assert script.references[0].original_caption == "Video 2"
    assert script.references[0].similarity_score == 0.99
    assert script.references[1].original_caption == "Video 1"


@pytest.mark.asyncio
async def test_search_viral_patterns_with_reranking() -> None:
    fake_embed = FakeEmbeddingPort()
    fake_vector = FakeVectorStorePort()
    fake_rerank = FakeRerankPort(reversed_order=True)

    await fake_vector.upsert(
        id="v1",
        vector=[0.1, 0.2, 0.3],
        metadata={"caption": "Early Bird", "hook_candidate": "Wake up!"},
        document="Doc 1",
    )
    await fake_vector.upsert(
        id="v2",
        vector=[0.1, 0.2, 0.3],
        metadata={"caption": "Night Owl", "hook_candidate": "Stay up!"},
        document="Doc 2",
    )

    use_case = SearchViralPatternsUseCase(
        embedding_port=fake_embed,
        vector_store_port=fake_vector,
        rerank_port=fake_rerank,
    )

    results = await use_case.execute(query="Night routines", top_k=2, use_rerank=True)
    assert len(results) == 2
    # Reranker should have prioritized v2 (reversed order)
    assert results[0].id == "v2"
    assert results[0].score == 0.99
    assert results[1].id == "v1"
