from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryRecord:
    id: str
    tenant_id: str
    user_id: str
    content: str
    sensitivity: str
    consented: bool

class MemoryManager:
    def __init__(self) -> None: self.records: list[MemoryRecord] = []
    def remember(self, record: MemoryRecord) -> None:
        if not record.consented or record.sensitivity == "sensitive": raise ValueError("memory write rejected by policy")
        self.records.append(record)
    def retrieve(self, tenant_id: str, user_id: str, query: str) -> list[MemoryRecord]:
        return [r for r in self.records if r.tenant_id == tenant_id and r.user_id == user_id and query.lower() in r.content.lower()][:5]
