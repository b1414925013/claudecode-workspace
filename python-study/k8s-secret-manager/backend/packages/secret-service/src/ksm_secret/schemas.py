from pydantic import BaseModel, Field
from typing import Optional


class SecretQuery(BaseModel):
    env_id: int = Field(..., ge=1)
    namespace: str = Field(..., min_length=1)


class SecretDetailQuery(SecretQuery):
    secret_name: str = Field(..., min_length=1)
    key: str = Field(..., min_length=1)


class SyncRequest(BaseModel):
    env_id: int = Field(..., ge=1)
    namespace: str = Field(..., min_length=1)


class CredentialCreate(BaseModel):
    env_id: int = Field(..., ge=1)
    service_name: str = Field(..., max_length=128)
    db_type: str = Field(default="mysql", pattern="^(mysql|redis|postgresql|mongodb|other)$")
    host: str = Field(..., max_length=256)
    port: int = Field(..., ge=1, le=65535)
    database_name: Optional[str] = None
    username: str = Field(..., max_length=128)
    password: str = Field(..., min_length=1)
    extra_params: Optional[dict] = None
    description: Optional[str] = None


class CredentialUpdate(BaseModel):
    service_name: Optional[str] = None
    db_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    extra_params: Optional[dict] = None
    description: Optional[str] = None
