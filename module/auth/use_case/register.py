"""Register use case."""

from dataclasses import dataclass

from core.security import hash_password
from module.auth.domain.entities.user import UserEntity
from module.auth.domain.exceptions import EmailAlreadyExistsException
from module.auth.port.user_repo import IUserRepository


@dataclass
class UserRegisterInputDTO:
    email: str
    password: str
    name: str | None = None


class RegisterUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, payload: UserRegisterInputDTO) -> UserEntity:
        # Check if user already exists
        existing_user = await self._user_repo.get_by_email(payload.email)
        if existing_user:
            raise EmailAlreadyExistsException(payload.email)

        # Create user entity with hashed password
        hashed = hash_password(payload.password)
        new_user = UserEntity(
            email=payload.email,
            password_hash=hashed,
            name=payload.name,
            role="user",
        )

        created_user = await self._user_repo.add(new_user)
        return created_user
