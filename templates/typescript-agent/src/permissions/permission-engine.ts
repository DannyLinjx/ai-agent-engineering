import { AgentState } from "../contracts.js";
import { Tool } from "../tools/registry.js";
export type PermissionDecision = "ALLOW" | "DENY" | "ASK";
export class PermissionEngine { decide(tool: Tool, _input: unknown, _state: AgentState): PermissionDecision { if (tool.riskLevel === "critical") return "DENY"; if (tool.riskLevel === "high" || tool.category === "communication") return "ASK"; return tool.category === "read" ? "ALLOW" : "ASK"; } }
