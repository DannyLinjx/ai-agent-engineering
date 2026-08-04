export type HookEvent = "PreSessionStart" | "PostSessionStart" | "PreContextBuild" | "PostContextBuild" | "PreModelCall" | "PostModelCall" | "PreToolUse" | "PostToolUse" | "OnToolError" | "PreCompact" | "PostCompact" | "PreFinalAnswer" | "PostFinalAnswer" | "OnSessionEnd";
export interface HookContext { tenantId: string; userId: string; sessionId: string; runId: string; signal: AbortSignal; }
export interface HookResult<T> { action: "continue" | "deny" | "annotate"; value: T; reason?: string; }
export interface AgentHook<T> { name: string; event: HookEvent; priority: number; timeoutMs: number; failureMode: "closed" | "open"; run(value: T, context: HookContext): Promise<HookResult<T>>; }
