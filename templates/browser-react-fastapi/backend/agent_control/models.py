from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=12, max_length=1024)


class PrincipalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: str
    user_id: str
    role: str


class ExperienceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile: str
    surfaces: list[str]
    role: str
