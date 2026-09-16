"""Integration tests for Chatbot RAG endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from module.video_rag.infra.llm.self_hosted_llm import SelfHostedLLMAdapter

client = TestClient(app)


async def _mock_stream_chat(*args, **kwargs):
    yield "Xin "
    yield "chào! "
    yield "Đây là câu trả lời."


def test_chat_non_streaming_turn_and_session_lifecycle() -> None:
    """Verify full lifecycle of non-streaming chat turns, session history, and deletion."""
    with patch.object(SelfHostedLLMAdapter, "stream_chat", side_effect=_mock_stream_chat):
        # Turn 1: Start conversation
        req1 = {
            "message": "Gợi ý hook cho video viral về năng suất làm việc",
            "top_k_references": 2,
        }
        res1 = client.post("/api/v1/chat", json=req1)
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["success"] is True
        session_id = data1["data"]["session_id"]
        assert session_id != ""
        assert data1["data"]["role"] == "assistant"
        assert len(data1["data"]["reply"]) > 0

        # Turn 2: Continue conversation with session_id
        req2 = {
            "message": "Viết chi tiết kịch bản cho ý tưởng này",
            "session_id": session_id,
            "top_k_references": 2,
        }
        res2 = client.post("/api/v1/chat", json=req2)
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["data"]["session_id"] == session_id

        # Get session details
        detail_res = client.get(f"/api/v1/chat/sessions/{session_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["success"] is True
        assert detail_data["data"]["session_id"] == session_id
        # 2 user messages + 2 assistant messages = 4 messages
        assert detail_data["data"]["message_count"] == 4

        # List active sessions
        list_res = client.get("/api/v1/chat/sessions")
        assert list_res.status_code == 200
        list_data = list_res.json()
        assert session_id in list_data["data"]["session_ids"]

        # Delete session
        del_res = client.delete(f"/api/v1/chat/sessions/{session_id}")
        assert del_res.status_code == 200
        assert del_res.json()["data"]["deleted"] is True

        # Confirm 404 after deletion
        not_found_res = client.get(f"/api/v1/chat/sessions/{session_id}")
        assert not_found_res.status_code == 404


def test_chat_streaming_endpoint() -> None:
    """Verify SSE streaming endpoint emits chunks, metadata, and done token."""
    with patch.object(SelfHostedLLMAdapter, "stream_chat", side_effect=_mock_stream_chat):
        req = {
            "message": "Cho tôi 3 hook kịch tính về đầu tư tài chính cá nhân",
            "top_k_references": 2,
        }
        res = client.post("/api/v1/chat/stream", json=req)
        assert res.status_code == 200
        assert "text/event-stream" in res.headers.get("content-type", "")

        content = res.text
        # Check that events exist in the stream
        assert "data: " in content
        assert '"event": "metadata"' in content
        assert '"event": "token"' in content
        assert "[DONE]" in content


def test_chat_empty_message_validation() -> None:
    """Verify 422/400 validation error when sending empty message."""
    res = client.post("/api/v1/chat", json={"message": ""})
    assert res.status_code == 422

    res_stream = client.post("/api/v1/chat/stream", json={"message": ""})
    assert res_stream.status_code == 422


def test_nonexistent_session_404() -> None:
    """Verify 404 on invalid session ID retrieval and deletion."""
    res_get = client.get("/api/v1/chat/sessions/invalid-id-xyz-999")
    assert res_get.status_code == 404

    res_del = client.delete("/api/v1/chat/sessions/invalid-id-xyz-999")
    assert res_del.status_code == 404
