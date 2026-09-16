"""Integration tests for FastAPI REST endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from module.video_rag.domain.entities.reference_pattern import (
    ReferencedPattern,
    SimilarVideoContext,
)
from module.video_rag.domain.entities.viral_script import (
    CallToAction,
    Hook,
    Scene,
    ViralScript,
)
from module.video_rag.domain.value_objects.hook_type import HookType
from module.video_rag.domain.value_objects.platform_target import PlatformTarget
from module.video_rag.infra.embeddings.self_hosted_embed import (
    SelfHostedEmbeddingAdapter,
)
from module.video_rag.infra.llm.self_hosted_llm import SelfHostedLLMAdapter
from module.video_rag.infra.rerank.dut_ai_rerank_adapter import DutAiRerankAdapter
from module.video_rag.infra.vector_store.pgvector_adapter import PgVectorAdapter
from module.video_rag.port.rerank_port import RerankedDocument

client = TestClient(app)


def test_root_endpoint() -> None:
    """Verify root GET / endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "app_name" in json_data["data"]


def test_health_check_endpoint() -> None:
    """Verify GET /api/v1/health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "healthy"
    assert "total_indexed_patterns" in json_data["data"]


def test_ingest_endpoint_removed() -> None:
    """Verify POST /api/v1/ingest has been removed and returns 404."""
    res = client.post("/api/v1/ingest", json={"file_path": "test.json"})
    assert res.status_code == 404


def test_full_pipeline_search_generate() -> None:
    """Verify search and RAG generate pipeline:
    1. Search benchmark patterns by query.
    2. RAG-generate 45s viral TikTok script with storyboard and AI prompts.
    """

    async def mock_embed_batch(texts: list[str]) -> list[list[float]]:
        # Deterministic 1024-dimension vectors for testing
        return [[0.05 * (i + 1) for i in range(1024)] for _ in texts]

    async def mock_generate_script(*args, **kwargs) -> ViralScript:
        return ViralScript(
            title="The 2-Minute Rule",
            target_niche="Students and professionals",
            platform=PlatformTarget.TIKTOK,
            target_duration_seconds=45,
            hook=Hook(
                hook_type=HookType.CONTRARIAN,
                script="Stop planning for hours!",
                visual_action="Snap zoom into camera",
                retention_rationale="Pattern interrupt curiosity",
                duration_seconds=4,
            ),
            scenes=[
                Scene(
                    scene_number=1,
                    time_range="00:00 - 00:04",
                    narration="Hook narration",
                    visual_action="Face close up",
                    image_prompt="Moody lighting portrait",
                    video_prompt="Zoom in cinematic",
                    audio_sfx_cue="Whoosh sound",
                ),
                Scene(
                    scene_number=2,
                    time_range="00:04 - 00:20",
                    narration="Body explanation",
                    visual_action="Desk work",
                    image_prompt="Frustrated worker",
                    video_prompt="Glitch cut",
                    audio_sfx_cue="Clock ticking",
                ),
                Scene(
                    scene_number=3,
                    time_range="00:20 - 00:45",
                    narration="Conclusion",
                    visual_action="Success gesture",
                    image_prompt="Happy person",
                    video_prompt="Orbit shot",
                    audio_sfx_cue="Chime sound",
                ),
            ],
            call_to_action=CallToAction(
                script="Save this video now!",
                visual_cue="Bookmark icon",
            ),
            references=[
                ReferencedPattern(
                    original_caption="Habit Loop",
                    matched_hook="2-min trick",
                    minio_video_url="https://minio.example.com/videos/v1.mp4",
                    similarity_score=0.92,
                    summary="Test summary",
                    image_url="https://minio.example.com/images/v1.jpg",
                )
            ],
            suggested_hashtags=["#discipline", "#habits"],
        )

    async def mock_rerank(query: str, documents: list[str], top_n: int = 3) -> list[RerankedDocument]:
        return [RerankedDocument(index=i, score=0.95 - (i * 0.1), text=doc) for i, doc in enumerate(documents[:top_n])]

    async def mock_vector_search(self, query_vector: list[float], top_k: int = 5) -> list[SimilarVideoContext]:
        return [
            SimilarVideoContext(
                id="p1",
                document="Content about habit and 2-minute rule",
                metadata={"caption": "Habit Loop", "hook_candidate": "2-min trick"},
                score=0.92,
            )
        ]

    async def mock_initialize(self) -> None:
        return None

    with (
        patch.object(SelfHostedEmbeddingAdapter, "embed_batch", side_effect=mock_embed_batch),
        patch.object(SelfHostedLLMAdapter, "generate_script", side_effect=mock_generate_script),
        patch.object(DutAiRerankAdapter, "rerank", side_effect=mock_rerank),
        patch.object(PgVectorAdapter, "initialize", new=mock_initialize),
        patch.object(PgVectorAdapter, "search", new=mock_vector_search),
    ):
        # 1. Search Patterns
        search_payload = {"query": "discipline habit", "top_k": 3}
        search_res = client.post("/api/v1/search-patterns", json=search_payload)
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["success"] is True
        assert len(search_data["data"]) >= 1

        # 2. Generate Script
        gen_payload = {
            "topic": "How to apply the 2-minute rule to beat procrastination",
            "target_audience": "Working professionals and students",
            "duration_seconds": 45,
            "platform": "tiktok",
            "hook_style": "contrarian",
            "top_k_patterns": 2,
        }
        gen_res = client.post("/api/v1/generate-script", json=gen_payload)
        assert gen_res.status_code == 200
        gen_data = gen_res.json()
        assert gen_data["success"] is True

        script = gen_data["data"]
        assert script["title"] != ""
        assert script["platform"] == "tiktok"
        assert script["target_duration_seconds"] == 45
        # Verify Hook
        assert script["hook"]["script"] != ""
        assert script["hook"]["retention_rationale"] != ""
        # Verify Storyboard
        assert len(script["scenes"]) >= 3
        assert script["scenes"][0]["image_prompt"] != ""
        assert script["scenes"][0]["video_prompt"] != ""
        assert script["scenes"][0]["audio_sfx_cue"] != ""
        # Verify CTA and Benchmark References
        assert script["call_to_action"]["script"] != ""
        assert len(script["references"]) >= 1
        assert "https://minio" in script["references"][0]["minio_video_url"]
