from dataclasses import dataclass, field
from typing import Generic, Literal, Protocol, TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")

@dataclass(frozen=True)
class ToolContext:
    tenant_id: str
    user_id: str
    session_id: str
    run_id: str
    workspace: str
    deadline_epoch_ms: int

@dataclass
class ToolResult(Generic[OutputT]):
    status: Literal["success", "error", "cancelled"]
    summary: str
    data: OutputT | None = None
    artifact_refs: list[str] = field(default_factory=list)
    retryable: bool = False
    side_effect_receipt: str | None = None
    error_code: str | None = None

class AgentTool(Protocol[InputT, OutputT]):
    name: str
    version: str
    description: str
    input_schema: dict[str, object]
    category: Literal["read", "write", "exec", "network", "database", "browser", "communication"]
    risk_level: Literal["low", "medium", "high", "critical"]
    timeout_seconds: int
    max_output_bytes: int
    def execute(self, input_data: InputT, context: ToolContext) -> ToolResult[OutputT]: ...
