"""Unit tests for DutAiRerankAdapter."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from module.video_rag.infra.rerank.dut_ai_rerank_adapter import DutAiRerankAdapter


@pytest.mark.asyncio
async def test_rerank_success() -> None:
    """Test successful rerank response parsing and sorting."""
    adapter = DutAiRerankAdapter(
        api_base_url="https://textembedding.dutai.io.vn",
        api_key="dutaiclb",
        fallback_mode=False,
    )

    mock_response_data = [
        {"index": 1, "score": 0.985, "text": "Hà Nội là thủ đô của Việt Nam."},
        {"index": 0, "score": 0.120, "text": "Đà Nẵng là thành phố biển."},
        {"index": 2, "score": 0.005, "text": "Khí hậu tại Sa Pa rất mát."},
    ]

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
        results = await adapter.rerank(
            query="Thủ đô Việt Nam",
            documents=[
                "Đà Nẵng là thành phố biển.",
                "Hà Nội là thủ đô của Việt Nam.",
                "Khí hậu tại Sa Pa rất mát.",
            ],
            top_n=2,
        )

        assert len(results) == 2
        assert results[0].index == 1
        assert results[0].score == 0.985
        assert results[0].text == "Hà Nội là thủ đô của Việt Nam."
        assert results[1].index == 0
        assert results[1].score == 0.120

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["json"]["query"] == "Thủ đô Việt Nam"
        assert kwargs["headers"]["Authorization"] == "Bearer dutaiclb"


@pytest.mark.asyncio
async def test_rerank_enforces_batch_size_cap() -> None:
    """Test that candidate documents are capped to max_batch_size (32)."""
    adapter = DutAiRerankAdapter(max_batch_size=32)

    docs = [f"Doc {i}" for i in range(50)]

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = [{"index": 0, "score": 0.9, "text": "Doc 0"}]

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
        await adapter.rerank(query="test", documents=docs, top_n=3)
        _, kwargs = mock_post.call_args
        sent_texts = kwargs["json"]["texts"]
        assert len(sent_texts) == 32



@pytest.mark.asyncio
async def test_rerank_empty_documents() -> None:
    """Test that empty query or documents returns empty list immediately."""
    adapter = DutAiRerankAdapter()
    assert await adapter.rerank(query="", documents=["doc1"]) == []
    assert await adapter.rerank(query="query", documents=[]) == []


@pytest.mark.asyncio
async def test_rerank_fallback_mode_on_error() -> None:
    """Test graceful fallback ordering when endpoint is unavailable."""
    adapter = DutAiRerankAdapter(fallback_mode=True)

    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        results = await adapter.rerank(
            query="test query",
            documents=["Doc A", "Doc B", "Doc C"],
            top_n=2,
        )
        assert len(results) == 2
        assert results[0].text == "Doc A"
        assert results[0].score > results[1].score


@pytest.mark.asyncio
async def test_rerank_raises_when_fallback_disabled() -> None:
    """Test exception propagation when fallback_mode is False."""
    adapter = DutAiRerankAdapter(fallback_mode=False)

    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        with pytest.raises(httpx.ConnectError):
            await adapter.rerank(
                query="test query",
                documents=["Doc A", "Doc B"],
                top_n=2,
            )
