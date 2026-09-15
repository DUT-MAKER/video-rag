"""Integration tests for FastAPI REST endpoints."""

from fastapi.testclient import TestClient

from main import app

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


def test_full_pipeline_ingest_search_generate() -> None:
    """Verify full end-to-end flow:
    1. Ingest sample knowledge file data/samples/sample_viral_videos.json.
    2. Search benchmark patterns by query.
    3. RAG-generate 45s viral TikTok script with storyboard and AI prompts.
    """
    # 1. Ingest
    ingest_payload = {"file_path": "data/samples/sample_viral_videos.json"}
    ingest_res = client.post("/api/v1/ingest", json=ingest_payload)
    assert ingest_res.status_code == 200
    ingest_data = ingest_res.json()
    assert ingest_data["success"] is True
    assert ingest_data["data"]["total_indexed"] == 5

    # 2. Search Patterns
    search_payload = {"query": "discipline habit", "top_k": 3}
    search_res = client.post("/api/v1/search-patterns", json=search_payload)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["success"] is True
    assert len(search_data["data"]) >= 1

    # 3. Generate Script
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
