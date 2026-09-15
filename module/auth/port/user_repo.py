"""User repository interface port."""

from typing import Protocol

from module.auth.domain.entities.user import UserEntity


class IUserRepository(Protocol):
    """Interface protocol for UserRepository database operations."""

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        """Get a user entity by its integer ID."""
        ...

    async def get_by_email(self, email: str) -> UserEntity | None:
        """Get a user entity by its email address."""
        ...

    async def add(self, entity: UserEntity) -> UserEntity:
        """Add a new user entity to the store."""
        ...

    async def update(self, entity: UserEntity) -> UserEntity:
        """Update an existing user entity in the store."""
        ...

    async def flush(self) -> None:
        """Flush pending changes to the database."""
        ...
