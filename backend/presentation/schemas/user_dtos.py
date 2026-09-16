"""User and Auth Request/Response DTOs."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str | None = None


class UserLoginInput(BaseModel):
    email: EmailStr
    password: str


class UserUpdateInput(BaseModel):
    name: str | None = None
    avatar_url: str | None = None


class UserOut(BaseModel):
    id: int
    email: str
    role: str
    name: str | None = None
    avatar_url: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PresignUploadInput(BaseModel):
    key: str
    content_type: str = "application/octet-stream"


class UploadOut(BaseModel):
    key: str
    public_url: str
    presigned_url: str | None = None
