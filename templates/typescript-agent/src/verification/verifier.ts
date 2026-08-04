import { AgentState, VerificationResult } from "../contracts.js";
export class Verifier { async verify(state: AgentState, answer: string): Promise<VerificationResult> { const unmet = state.plan.filter(s => s.status !== "completed" && s.status !== "skipped").map(s => s.id); return { passed: answer.trim().length > 0 && unmet.length === 0, evidence: state.plan.flatMap(s => s.evidence), unmet }; } }
