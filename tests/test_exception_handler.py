import json

import pytest

from backend.main import create_app
from core.exceptions import AppException
from module.auth.domain.exceptions import InvalidCredentialsException


@pytest.mark.asyncio
async def test_invalid_credentials_returns_401_instead_of_handler_error():
    app = create_app()
    handler = app.exception_handlers[AppException]

    response = await handler(None, InvalidCredentialsException())

    assert response.status_code == 401
    assert json.loads(response.body)["message"] == "Email hoặc mật khẩu không chính xác"
