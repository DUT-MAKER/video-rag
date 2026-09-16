"""FastAPI dependency helpers for authentication and request context."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel

from core.jwt import decode_access_token


class UserContext(BaseModel):
    id: int
    role: str


async def get_current_user(request: Request) -> UserContext:
    """Dependency to retrieve and validate the current authenticated user."""
    # 1. Try to get token from Cookie
    access_token = request.cookies.get("access_token")

    # 2. Fallback: try to get from Authorization Header
    if not access_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]

    if not access_token:
        raise HTTPException(
            status_code=401, detail="Chưa xác thực: Không tìm thấy token"
        )

    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Chưa xác thực: Phiên làm việc đã hết hạn hoặc không hợp lệ",
        )

    uid = payload.get("user_id")
    role = payload.get("role")

    if uid is None or role is None:
        raise HTTPException(
            status_code=401, detail="Chưa xác thực: Payload token không hợp lệ"
        )

    return UserContext(
        id=int(uid),
        role=role,
    )


def require_roles(*allowed_roles: str):
    """Dependency factory to restrict access to specific user roles."""

    async def dependency(
        user: Annotated[UserContext, Depends(get_current_user)],
    ) -> UserContext:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403, detail="Không có quyền truy cập chức năng này"
            )
        return user

    return dependency


CurrentUser = Annotated[UserContext, Depends(get_current_user)]
AdminUser = Annotated[UserContext, Depends(require_roles("admin"))]
