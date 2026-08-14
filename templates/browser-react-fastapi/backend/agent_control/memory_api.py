from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .auth import Principal


@dataclass(frozen=True)
class MemoryScope:
    tenant_id: str
    user_id: str
    project_id: str = "default"


class MemoryPort(Protocol):
    def list(self, scope: MemoryScope) -> list[Any]: ...
    def soft_delete(self, scope: MemoryScope, record_id: str) -> bool: ...
    def export_records(self, scope: MemoryScope, *, format: str = "json") -> str: ...


class MemoryProjectionService:
    def __init__(self, port: MemoryPort) -> None:
        self.port = port

    @staticmethod
    def _scope(principal: Principal) -> MemoryScope:
        return MemoryScope(principal.tenant_id, principal.user_id)

    def list(self, principal: Principal) -> list[dict[str, Any]]:
        projections = []
        for record in self.port.list(self._scope(principal)):
            projections.append(
                {
                    "id": record.id,
                    "summary": record.summary,
                    "memory_type": record.memory_type,
                    "source": record.source,
                    "evidence_refs": list(record.evidence_refs),
                    "confidence": record.confidence,
                    "sensitivity": record.sensitivity,
                    "status": record.status,
                }
            )
        return projections

    def delete(self, principal: Principal, record_id: str) -> bool:
        return self.port.soft_delete(self._scope(principal), record_id)

    def export(self, principal: Principal, *, format: str = "json") -> str:
        return self.port.export_records(self._scope(principal), format=format)
