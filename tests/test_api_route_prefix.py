from backend.main import app


def test_api_v1_routes_are_not_prefixed_twice() -> None:
    paths = app.openapi()["paths"]

    assert "/api/v1/health" in paths
    assert "/api/v1/auth/register" in paths
    assert "/api/v1/crawler/jobs" in paths
    assert "/api/v1/api/v1/health" not in paths
