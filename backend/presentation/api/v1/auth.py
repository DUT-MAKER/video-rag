"""Auth router."""

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Response, status

from backend.presentation.schemas.user_dtos import (
    TokenOut,
    UserLoginInput,
    UserOut,
    UserRegisterInput,
)
from module.auth.use_case.login import LoginUseCase, UserLoginInputDTO
from module.auth.use_case.register import RegisterUseCase, UserRegisterInputDTO

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, access_token: str):
    """Utility to set HTTP-only cookie for JWT authentication."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
@inject
async def register(
    payload: UserRegisterInput,
    use_case: FromDishka[RegisterUseCase],
):
    """Registers a new user."""
    dto = UserRegisterInputDTO(
        email=str(payload.email),
        password=payload.password,
        name=payload.name,
    )
    user_entity = await use_case.execute(dto)
    return UserOut.model_validate(user_entity)


@router.post("/login", response_model=TokenOut)
@inject
async def login(
    payload: UserLoginInput,
    response: Response,
    use_case: FromDishka[LoginUseCase],
):
    """Logs in an existing user, setting a cookie and returning JWT."""
    dto = UserLoginInputDTO(
        email=str(payload.email),
        password=payload.password,
    )
    token_out = await use_case.execute(dto)
    _set_auth_cookie(response, token_out.access_token)
    return TokenOut(access_token=token_out.access_token, token_type=token_out.token_type)


@router.post("/logout")
async def logout(response: Response):
    """Logs out the current user by clearing the auth cookie."""
    response.delete_cookie("access_token")
    return {"is_success": True, "detail": "Đăng xuất thành công"}
