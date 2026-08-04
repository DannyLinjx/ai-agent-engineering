from .contracts import AgentState, VerificationResult

class Verifier:
    def verify(self, state: AgentState, answer: str) -> VerificationResult:
        unmet = [s.id for s in state.plan if s.status not in {"completed", "skipped"}]
        return VerificationResult(bool(answer.strip()) and not unmet, [e for s in state.plan for e in s.evidence], unmet)
