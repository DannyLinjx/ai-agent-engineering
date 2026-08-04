from dataclasses import dataclass, field

@dataclass(frozen=True)
class SubAgentTask:
    id: str
    objective: str
    max_steps: int
    max_tokens: int
    allowed_tools: list[str]

@dataclass
class SubAgentResult:
    task_id: str
    status: str
    summary: str
    evidence: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
