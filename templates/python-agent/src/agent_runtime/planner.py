from dataclasses import dataclass, field
from typing import Protocol
from .contracts import PlanStep

@dataclass
class AgentPlan:
    goal: str
    steps: list[PlanStep]
    completion_criteria: list[str]
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

class Planner(Protocol):
    def create(self, objective: str) -> AgentPlan: ...
    def revise(self, plan: AgentPlan, evidence: list[str]) -> AgentPlan: ...
