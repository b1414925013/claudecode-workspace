from pydantic import BaseModel, Field
from typing import Optional


class JsonFormatInput(BaseModel):
    input: str = Field(..., max_length=65535)
    indent: int = Field(default=2, ge=1, le=8)


class ToolInput(BaseModel):
    input: str = Field(..., max_length=65535)


class RegexTestInput(BaseModel):
    pattern: str = Field(..., max_length=1024)
    text: str = Field(..., max_length=65535)
    flags: str = ""


class PortCheckInput(BaseModel):
    host: str = Field(..., max_length=256)
    port: int = Field(..., ge=1, le=65535)
    timeout: int = Field(default=3, ge=1, le=30)


class TimestampInput(BaseModel):
    value: str = Field(..., max_length=64)


class LinkCreate(BaseModel):
    title: str = Field(..., max_length=128)
    url: str = Field(..., max_length=512)
    icon: str = "Link"
    category: str = "default"
    sort_order: int = 0


class LinkUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    sort_order: Optional[int] = None
