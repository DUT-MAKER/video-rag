"""Integration tests for Chatbot Web UI endpoints."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_chat_ui_serves_html() -> None:
    """Verify GET /chat endpoint serves valid HTML content."""
    response = client.get("/chat")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "ViralCopilot" in response.text
    assert "Viral Video AI Co-Pilot" in response.text


def test_ui_redirect_to_chat() -> None:
    """Verify GET /ui redirects to /chat."""
    response = client.get("/ui", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/chat"


def test_static_assets_accessible() -> None:
    """Verify static assets are served properly."""
    res_css = client.get("/static/styles.css")
    assert res_css.status_code == 200
    assert "--bg-base" in res_css.text

    res_js = client.get("/static/app.js")
    assert res_js.status_code == 200
    assert "ViralCopilot AI" in res_js.text
