from dataclasses import dataclass, field
import re

@dataclass(frozen=True)
class TraceEvent:
    event_type: str
    tenant_id: str
    user_id: str
    session_id: str
    run_id: str
    agent_id: str
    status: str
    data: dict[str, object] = field(default_factory=dict)

def redact(value: str) -> str:
    return re.sub(r"(?i)(token|password|secret|authorization)\s*[:=]\s*\S+", "[REDACTED]", value)
