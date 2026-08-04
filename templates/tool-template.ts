export type ToolCategory = "read" | "write" | "exec" | "network" | "database" | "browser" | "communication";
export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface ToolContext {
  tenantId: string; userId: string; sessionId: string; runId: string;
  workspace: string; signal: AbortSignal; deadline: number;
}

export interface ToolResult<T> {
  status: "success" | "error" | "cancelled";
  data?: T; summary: string; artifactRefs: string[];
  sideEffectReceipt?: string; retryable: boolean;
  error?: { code: string; message: string };
}

export interface AgentTool<I, O> {
  readonly name: string; readonly version: string; readonly description: string;
  readonly inputSchema: Record<string, unknown>; readonly category: ToolCategory;
  readonly riskLevel: RiskLevel; readonly timeoutMs: number; readonly maxOutputBytes: number;
  execute(input: I, context: ToolContext): Promise<ToolResult<O>>;
}
