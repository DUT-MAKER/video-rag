"""SQLAlchemy User Model."""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from core.datetime_utils import now_ict
from module.auth.domain.entities.user import UserEntity

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str] = mapped_column()
    name: Mapped[str | None] = mapped_column(nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(default="user", server_default="user")
    created_at: Mapped[datetime] = mapped_column(default=now_ict)

    def to_entity(self) -> UserEntity:
        """Converts the SQLAlchemy model to a domain entity."""
        return UserEntity(
            id=self.id,
            email=self.email,
            password_hash=self.password_hash,
            name=self.name,
            avatar_url=self.avatar_url,
            role=self.role,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "User":
        """Creates an SQLAlchemy model from a domain entity."""
        return cls(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            name=entity.name,
            avatar_url=entity.avatar_url,
            role=entity.role,
            created_at=entity.created_at or now_ict(),
        )
