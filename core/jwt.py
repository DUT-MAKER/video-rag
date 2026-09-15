"""JWT creation and decoding utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from loguru import logger

from core.config import auth_settings


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Creates a JWT access token containing the payload data."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=auth_settings.expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, auth_settings.secret_key, algorithm=auth_settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(
            token, auth_settings.secret_key, algorithms=[auth_settings.algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT Token: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error decoding JWT: {e}")
        return None
