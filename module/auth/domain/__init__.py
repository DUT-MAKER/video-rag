"""Auth domain package."""

from .entities.user import UserEntity
from .exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    UserNotFoundException,
)

__all__ = [
    "UserEntity",
    "UserNotFoundException",
    "EmailAlreadyExistsException",
    "InvalidCredentialsException",
]
