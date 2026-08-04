from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeConfig:
    max_steps: int
    max_replans: int
    task_timeout_seconds: int
    tool_timeout_seconds: int
    token_budget: int
    cost_budget_usd: float
    max_repeated_actions: int
    def validate(self) -> "RuntimeConfig":
        if self.max_steps < 1 or self.task_timeout_seconds < 1 or self.token_budget < 1 or self.cost_budget_usd < 0: raise ValueError("invalid runtime config")
        return self
