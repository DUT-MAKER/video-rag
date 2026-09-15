"""SQLAlchemy implementation of IUserRepository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from module.auth.domain.entities.user import UserEntity
from module.auth.infra.persistence.models.user import User
from module.auth.port.user_repo import IUserRepository


class UserRepository(IUserRepository):
    """SQLAlchemy implementation of the IUserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return m.to_entity() if m else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        return m.to_entity() if m else None

    async def add(self, entity: UserEntity) -> UserEntity:
        m = User.from_entity(entity)
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return m.to_entity()

    async def update(self, entity: UserEntity) -> UserEntity:
        stmt = select(User).where(User.id == entity.id)
        result = await self._session.execute(stmt)
        m = result.scalar_one_or_none()
        if m:
            m.email = entity.email
            m.password_hash = entity.password_hash
            m.name = entity.name
            m.avatar_url = entity.avatar_url
            m.role = entity.role
            await self._session.flush()
            await self._session.refresh(m)
            return m.to_entity()
        return entity

    async def flush(self) -> None:
        await self._session.flush()
