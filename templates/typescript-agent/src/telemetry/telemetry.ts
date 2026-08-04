export interface TraceEvent { eventType: string; tenantId: string; userId: string; sessionId: string; runId: string; agentId: string; status: string; data: Record<string, unknown>; }
export interface Telemetry { emit(event: TraceEvent): void; increment(metric: string, value: number, labels: Record<string, string>): void; }
export const redact = (value: string): string => value.replace(/(token|password|secret|authorization)\s*[:=]\s*\S+/gi, "[REDACTED]");
