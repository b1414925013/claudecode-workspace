from pydantic import BaseModel, Field
from typing import Optional, List


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=4, max_length=128)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str = Field(default="developer", pattern="^(admin|developer)$")


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|developer)$")
    is_active: Optional[bool] = None


class ResetPassword(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)


class EnvPermissionUpdate(BaseModel):
    env_ids: List[int]
