export type RunStatus = "created" | "planning" | "running" | "waiting_approval" | "verifying" | "completed" | "failed" | "cancelled";
export interface PlanStep { id: string; objective: string; status: "pending" | "running" | "completed" | "failed" | "skipped"; verificationMethod: string; evidence: string[]; }
export interface AgentState { runId: string; tenantId: string; userId: string; sessionId: string; agentId: string; objective: string; plan: PlanStep[]; currentStep: number; stepCount: number; maxSteps: number; tokenUsage: number; status: RunStatus; observations: string[]; errors: string[]; }
export type ModelDecision = { kind: "respond"; answer: string } | { kind: "tool_call"; tool: string; input: unknown; reason: string } | { kind: "replan"; reason: string } | { kind: "fail"; reason: string };
export interface ModelGateway { decide(state: Readonly<AgentState>, signal: AbortSignal): Promise<ModelDecision>; }
export interface VerificationResult { passed: boolean; evidence: string[]; unmet: string[]; }
