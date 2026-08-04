from dataclasses import dataclass, field
from typing import Any, Literal

@dataclass
class PlanStep:
    id: str
    objective: str
    verification_method: str
    status: Literal["pending", "running", "completed", "failed", "skipped"] = "pending"
    evidence: list[str] = field(default_factory=list)

@dataclass
class AgentState:
    run_id: str
    tenant_id: str
    user_id: str
    session_id: str
    agent_id: str
    objective: str
    plan: list[PlanStep]
    max_steps: int = 24
    current_step: int = 0
    step_count: int = 0
    token_usage: int = 0
    status: Literal["created", "planning", "running", "waiting_approval", "verifying", "completed", "failed", "cancelled"] = "created"
    observations: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class ModelDecision:
    kind: Literal["respond", "tool_call", "replan", "fail"]
    answer: str | None = None
    tool: str | None = None
    input_data: Any = None
    reason: str | None = None

@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    evidence: list[str]
    unmet: list[str]
