from backend.main import app
from core.config import app_settings, auth_settings, db_settings, vector_store_settings
from core.jwt import create_access_token, decode_access_token
from core.security import hash_password, verify_password


def test_core_security():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)

    token = create_access_token({"user_id": 1, "role": "admin"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["user_id"] == 1
    assert payload["role"] == "admin"


def test_app_initialization():
    assert app.title == app_settings.name
    assert db_settings.url is not None
    assert auth_settings.algorithm == "HS256"
    assert vector_store_settings.table_name == "viral_video_embeddings"
    routes = list(app.openapi()["paths"].keys())

    assert "/api/v1/health" in routes
    assert "/api/v1/auth/register" in routes
    assert "/api/v1/auth/login" in routes
    assert "/api/v1/me" in routes
    assert "/api/v1/uploads" in routes
    assert "/api/v1/ingest" in routes
    assert "/api/v1/search" in routes
    assert "/api/v1/generate" in routes
    assert "/api/v1/chat" in routes
