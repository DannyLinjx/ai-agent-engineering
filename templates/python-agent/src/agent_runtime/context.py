from dataclasses import dataclass
from .contracts import AgentState

@dataclass(frozen=True)
class ContextPacket:
    objective: str
    current_step: str | None
    observations: list[str]
    remaining_steps: int

class ContextBuilder:
    def build(self, state: AgentState) -> ContextPacket:
        step = state.plan[state.current_step].objective if state.current_step < len(state.plan) else None
        return ContextPacket(state.objective, step, state.observations[-12:], state.max_steps - state.step_count)
