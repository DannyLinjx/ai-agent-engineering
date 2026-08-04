from copy import deepcopy
from typing import Protocol
from .contracts import AgentState

class CheckpointRepository(Protocol):
    def save(self, state: AgentState) -> None: ...
    def load(self, run_id: str) -> AgentState | None: ...

class InMemoryCheckpointRepository:
    def __init__(self) -> None: self.states: dict[str, AgentState] = {}
    def save(self, state: AgentState) -> None: self.states[state.run_id] = deepcopy(state)
    def load(self, run_id: str) -> AgentState | None: return deepcopy(self.states.get(run_id))
