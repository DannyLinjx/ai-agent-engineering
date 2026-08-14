from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class MemoryScope:
    tenant_id: str
    user_id: str
    project_id: str = "default"


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    tenant_id: str
    user_id: str
    content: Mapping[str, Any] | str
    summary: str = ""
    memory_type: str = "fact"
    source: str = "user_statement"
    evidence_refs: tuple[str, ...] = ()
    confidence: float = 1.0
    importance: float = 0.5
    sensitivity: str = "internal"
    consent_basis: str = "none"
    consented: bool | None = None
    policy_version: str = "1.0"
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    expires_at: datetime | None = None
    status: str = "active"
    project_id: str = "default"
    conflict_with_ids: tuple[str, ...] = ()
    supersedes_id: str | None = None
    embedding_model: str | None = None
    embedding_version: str | None = None

    @property
    def scope(self) -> MemoryScope:
        return MemoryScope(self.tenant_id, self.user_id, self.project_id)


@dataclass(frozen=True)
class MemoryQuery:
    scope: MemoryScope
    text: str
    limit: int = 5
    memory_types: tuple[str, ...] = ()
    as_of: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class MemorySearchResult:
    record: MemoryRecord
    score: float
    score_components: Mapping[str, float]
    source: str
    evidence_refs: tuple[str, ...]
    confidence: float


@dataclass(frozen=True)
class MemoryDecision:
    action: str
    reason: str
    policy_version: str = "1.0"
