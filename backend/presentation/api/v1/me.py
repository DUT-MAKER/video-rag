"""User profile (Me) router."""

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from backend.presentation.api.deps import CurrentUser
from backend.presentation.schemas.user_dtos import UserOut, UserUpdateInput
from module.auth.use_case.get_profile import GetProfileUseCase
from module.auth.use_case.update_profile import UpdateProfileUseCase, UserUpdateInputDTO

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=UserOut)
@inject
async def get_my_profile(
    current_user: CurrentUser,
    use_case: FromDishka[GetProfileUseCase],
):
    """Retrieves current authenticated user's profile information."""
    user = await use_case.execute(current_user.id)
    return UserOut.model_validate(user)


@router.put("", response_model=UserOut)
@inject
async def update_my_profile(
    payload: UserUpdateInput,
    current_user: CurrentUser,
    use_case: FromDishka[UpdateProfileUseCase],
):
    """Updates current authenticated user's profile information."""
    dto = UserUpdateInputDTO(name=payload.name, avatar_url=payload.avatar_url)
    user = await use_case.execute(current_user.id, dto)
    return UserOut.model_validate(user)
