"""Update profile use case."""

from dataclasses import dataclass

from module.auth.domain.entities.user import UserEntity
from module.auth.domain.exceptions import UserNotFoundException
from module.auth.port.user_repo import IUserRepository


@dataclass
class UserUpdateInputDTO:
    name: str | None = None
    avatar_url: str | None = None


class UpdateProfileUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: int, payload: UserUpdateInputDTO) -> UserEntity:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        if payload.name is not None:
            user.name = payload.name
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url

        updated_user = await self._user_repo.update(user)
        return updated_user
