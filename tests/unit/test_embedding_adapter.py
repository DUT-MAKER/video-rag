"""Unit tests for SelfHostedEmbeddingAdapter."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from module.video_rag.domain.exceptions import EmbeddingError
from module.video_rag.infra.embeddings.self_hosted_embed import (
    SelfHostedEmbeddingAdapter,
)


@pytest.mark.asyncio
async def test_embed_batch_success() -> None:
    """Verify embed_batch parses 200 response and extracts embeddings."""
    mock_response = httpx.Response(
        status_code=200,
        json={
            "data": [
                {"index": 0, "embedding": [0.1, 0.2, 0.3]},
                {"index": 1, "embedding": [0.4, 0.5, 0.6]},
            ]
        },
        request=httpx.Request("POST", "http://test/embeddings"),
    )

    adapter = SelfHostedEmbeddingAdapter(
        api_base_url="http://test",
        dimension=3,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await adapter.embed_batch(["text1", "text2"])

        assert len(result) == 2
        assert result[0] == [0.1, 0.2, 0.3]
        assert result[1] == [0.4, 0.5, 0.6]


@pytest.mark.asyncio
async def test_embed_text_success() -> None:
    """Verify embed_text calls embed_batch and returns single vector."""
    mock_response = httpx.Response(
        status_code=200,
        json={
            "data": [
                {"index": 0, "embedding": [0.1, 0.2, 0.3]},
            ]
        },
        request=httpx.Request("POST", "http://test/embeddings"),
    )

    adapter = SelfHostedEmbeddingAdapter(
        api_base_url="http://test",
        dimension=3,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await adapter.embed_text("sample")

        assert result == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_embed_batch_empty() -> None:
    """Verify empty input returns empty list immediately."""
    adapter = SelfHostedEmbeddingAdapter()
    result = await adapter.embed_batch([])
    assert result == []


@pytest.mark.asyncio
async def test_embed_batch_raises_on_http_error() -> None:
    """Verify EmbeddingError is raised when API returns non-200 and no fallback is returned."""
    mock_response = httpx.Response(
        status_code=500,
        text="Internal Server Error",
        request=httpx.Request("POST", "http://test/embeddings"),
    )

    adapter = SelfHostedEmbeddingAdapter(
        api_base_url="http://test",
        dimension=3,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with pytest.raises(EmbeddingError) as exc_info:
            await adapter.embed_batch(["some text"])

        assert "Embedding service returned HTTP 500" in str(exc_info.value)


@pytest.mark.asyncio
async def test_embed_batch_raises_on_network_failure() -> None:
    """Verify EmbeddingError is raised on network connection failure without hash fallback."""
    adapter = SelfHostedEmbeddingAdapter(
        api_base_url="http://test",
        dimension=3,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectError("Connection refused")
        with pytest.raises(EmbeddingError) as exc_info:
            await adapter.embed_batch(["some text"])

        assert "Failed to generate embeddings" in str(exc_info.value)


@pytest.mark.asyncio
async def test_embed_batch_raises_on_mismatched_count() -> None:
    """Verify EmbeddingError is raised when response has fewer embeddings than inputs."""
    mock_response = httpx.Response(
        status_code=200,
        json={"data": [{"index": 0, "embedding": [0.1, 0.2, 0.3]}]},
        request=httpx.Request("POST", "http://test/embeddings"),
    )

    adapter = SelfHostedEmbeddingAdapter(
        api_base_url="http://test",
        dimension=3,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with pytest.raises(EmbeddingError) as exc_info:
            await adapter.embed_batch(["text1", "text2"])

        assert "Expected 2 embeddings, but received 1" in str(exc_info.value)
