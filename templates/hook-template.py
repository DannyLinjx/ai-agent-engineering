from dataclasses import dataclass
from typing import Generic, Literal, Protocol, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class HookContext:
    tenant_id: str
    user_id: str
    session_id: str
    run_id: str

@dataclass
class HookResult(Generic[T]):
    action: Literal["continue", "deny", "annotate"]
    value: T
    reason: str | None = None

class AgentHook(Protocol[T]):
    name: str
    event: str
    priority: int
    timeout_seconds: int
    failure_mode: Literal["closed", "open"]
    def run(self, value: T, context: HookContext) -> HookResult[T]: ...
