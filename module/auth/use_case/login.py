"""Login use case."""

from dataclasses import dataclass

from core.jwt import create_access_token
from core.security import verify_password
from module.auth.domain.exceptions import InvalidCredentialsException
from module.auth.port.user_repo import IUserRepository


@dataclass
class UserLoginInputDTO:
    email: str
    password: str


@dataclass
class TokenOutputDTO:
    access_token: str
    token_type: str = "bearer"


class LoginUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, payload: UserLoginInputDTO) -> TokenOutputDTO:
        user = await self._user_repo.get_by_email(payload.email)
        if not user:
            raise InvalidCredentialsException()

        if not verify_password(payload.password, user.password_hash):
            raise InvalidCredentialsException()

        token_data = {"user_id": user.id, "role": user.role}
        access_token = create_access_token(token_data)

        return TokenOutputDTO(access_token=access_token)
