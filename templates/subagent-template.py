from dataclasses import dataclass, field
from typing import Literal

@dataclass(frozen=True)
class SubAgentTask:
    id: str
    objective: str
    completion_criteria: list[str]
    max_steps: int
    max_tokens: int
    max_cost_usd: float
    deadline_epoch_ms: int
    allowed_tools: list[str]
    allowed_skills: list[str]
    workspace: str
    non_goals: list[str] = field(default_factory=list)

@dataclass
class SubAgentResult:
    task_id: str
    status: Literal["success", "partial", "failed"]
    summary: str
    findings: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    unresolved_issues: list[str] = field(default_factory=list)
    recommended_next_actions: list[str] = field(default_factory=list)
