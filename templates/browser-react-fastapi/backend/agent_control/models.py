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


class ConversationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=240)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    title: str
    status: str = "active"


class MessageCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=20_000)


class RunResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: str
    conversation_id: str
    status: str
    cancel_requested: bool
    created_at: str
    updated_at: str


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    run_id: str
    tool_name: str
    tool_version: str
    target: str
    risk: str
    evidence_refs: list[str]
    action_fingerprint: str
    expires_at: str
    decision: str


class ApprovalDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: str = Field(pattern="^(approved|rejected)$")


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    run_id: str
    filename: str
    media_type: str
    size_bytes: int = Field(ge=0)
    digest: str
    created_at: str


class MemoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    summary: str
    memory_type: str
    source: str
    evidence_refs: list[str]
    confidence: float = Field(ge=0, le=1)
    sensitivity: str
    status: str
