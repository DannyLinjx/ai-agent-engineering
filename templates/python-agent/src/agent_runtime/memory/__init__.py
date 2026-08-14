from __future__ import annotations

import json

from .contracts import (
    MemoryDecision,
    MemoryQuery,
    MemoryRecord,
    MemoryScope,
    MemorySearchResult,
)
from .policy import MemoryPolicy
from .retrieval import MemoryRetriever
from .sqlite_store import SQLiteMemoryStore


class MemoryManager:
    """Backward-compatible in-memory facade; durable profiles use MemoryPort stores."""

    def __init__(self, policy: MemoryPolicy | None = None) -> None:
        self.policy = policy or MemoryPolicy()
        self.records: list[MemoryRecord] = []

    def remember(self, record: MemoryRecord) -> None:
        decision = self.policy.evaluate(record)
        if decision.action != "accept":
            raise ValueError(f"memory write rejected by policy: {decision.reason}")
        self.records.append(record)

    def retrieve(self, tenant_id: str, user_id: str, query: str) -> list[MemoryRecord]:
        needle = query.casefold()
        return [
            record
            for record in self.records
            if record.tenant_id == tenant_id
            and record.user_id == user_id
            and needle in json.dumps(record.content, sort_keys=True, default=str).casefold()
        ][:5]


__all__ = [
    "MemoryDecision",
    "MemoryManager",
    "MemoryPolicy",
    "MemoryQuery",
    "MemoryRecord",
    "MemoryRetriever",
    "MemoryScope",
    "MemorySearchResult",
    "SQLiteMemoryStore",
]
