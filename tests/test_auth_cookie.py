from fastapi import Response

from backend.presentation.api.v1.auth import _set_auth_cookie


def test_auth_cookie_uses_configured_expiration() -> None:
    response = Response()

    _set_auth_cookie(response, "token")

    cookie = response.headers["set-cookie"]
    assert "access_token=token" in cookie
    assert "Max-Age=86400" in cookie
