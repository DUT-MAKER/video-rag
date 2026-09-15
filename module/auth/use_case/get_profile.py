"""Get profile use case."""

from module.auth.domain.entities.user import UserEntity
from module.auth.domain.exceptions import UserNotFoundException
from module.auth.port.user_repo import IUserRepository


class GetProfileUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: int) -> UserEntity:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user
