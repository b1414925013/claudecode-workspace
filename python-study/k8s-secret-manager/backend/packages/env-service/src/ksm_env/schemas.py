from pydantic import BaseModel, Field
from typing import Optional


class EnvCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=64, pattern="^[a-z0-9-]+$")
    label: str = Field(..., max_length=128)
    cluster_api: str = Field(..., max_length=256)
    kubeconfig: str = Field(..., min_length=10)
    kubeconfig_type: str = Field(default="content", pattern="^(content|path)$")
    namespace_config: dict = Field(default_factory=dict)
    k8s_sdk_mode: str = Field(default="auto", pattern="^(sdk|kubectl|auto)$")
    sort_order: int = 0


class EnvUpdate(BaseModel):
    label: Optional[str] = None
    cluster_api: Optional[str] = None
    kubeconfig: Optional[str] = None
    namespace_config: Optional[dict] = None
    k8s_sdk_mode: Optional[str] = None
    sort_order: Optional[int] = None
