from collections.abc import Callable
from typing import Protocol
from .contracts import AgentState, ModelDecision, VerificationResult
from .permissions import PermissionEngine
from .tools import ToolRegistry

class ModelGateway(Protocol):
    def decide(self, state: AgentState) -> ModelDecision: ...

class AgentRuntime:
    def __init__(self, model: ModelGateway, tools: ToolRegistry, permissions: PermissionEngine, verifier: Callable[[AgentState, str], VerificationResult], checkpoint: Callable[[AgentState], None]) -> None:
        self.model, self.tools, self.permissions, self.verifier, self.checkpoint = model, tools, permissions, verifier, checkpoint

    def run(self, state: AgentState, cancelled: Callable[[], bool] = lambda: False) -> tuple[AgentState, str | None]:
        while state.step_count < state.max_steps and not cancelled():
            state.status = "running"
            state.step_count += 1
            decision = self.model.decide(state)
            answer = self._apply(state, decision)
            self.checkpoint(state)
            if answer is not None:
                state.status = "verifying"
                result = self.verifier(state, answer)
                if result.passed:
                    state.status = "completed"
                    state.observations.extend(result.evidence)
                    return state, answer
                state.observations.extend(f"unmet:{item}" for item in result.unmet)
        state.status = "cancelled" if cancelled() else "failed"
        return state, None

    def _apply(self, state: AgentState, decision: ModelDecision) -> str | None:
        if decision.kind == "respond": return decision.answer or ""
        if decision.kind == "fail": state.errors.append(decision.reason or "model failure"); return None
        if decision.kind == "replan": state.observations.append(f"replan:{decision.reason}"); return None
        tool = self.tools.get(decision.tool or "")
        permission = self.permissions.decide(tool.category, tool.risk_level)
        if permission != "ALLOW": state.observations.append(f"permission:{permission}:{tool.name}"); return None
        state.observations.append(tool.execute(decision.input_data, state).summary)
        return None
