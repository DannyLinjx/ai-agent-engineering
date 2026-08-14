import { z } from "zod";

import { apiRequest } from "./client";

export const surfaceSchema = z.enum([
  "conversation", "run_inspector", "approvals", "artifacts", "memory",
  "overview", "runs", "audit", "models", "capabilities", "settings", "access", "health",
]);

export const principalSchema = z.object({
  tenant_id: z.string().min(1),
  user_id: z.string().min(1),
  role: z.enum(["user", "operator", "admin", "auditor"]),
});

export const experienceSchema = z.object({
  profile: z.enum(["browser_chat", "operations_console"]),
  surfaces: z.array(surfaceSchema).min(1),
  role: z.enum(["user", "operator", "admin", "auditor"]),
});

export const conversationSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  status: z.string().min(1),
});

export const runSchema = z.object({
  run_id: z.string().min(1),
  conversation_id: z.string().min(1),
  status: z.string().min(1),
  cancel_requested: z.boolean(),
  created_at: z.string().min(1),
  updated_at: z.string().min(1),
});

export const approvalSchema = z.object({
  id: z.string().min(1), run_id: z.string().min(1), tool_name: z.string().min(1), tool_version: z.string().min(1),
  target: z.string(), risk: z.string().min(1), evidence_refs: z.array(z.string()), action_fingerprint: z.string().min(1),
  expires_at: z.string().min(1), decision: z.string().min(1),
});

export const artifactSchema = z.object({
  id: z.string().min(1), run_id: z.string().min(1), filename: z.string().min(1), media_type: z.string().min(1),
  size_bytes: z.number().int().nonnegative(), digest: z.string().min(1), created_at: z.string().min(1),
});

export const memorySchema = z.object({
  id: z.string().min(1), summary: z.string(), memory_type: z.string().min(1), source: z.string().min(1),
  evidence_refs: z.array(z.string()), confidence: z.number().min(0).max(1), sensitivity: z.string().min(1), status: z.string().min(1),
});

export type RunProjection = z.infer<typeof runSchema>;

export function login(tenantId: string, username: string, password: string) {
  return apiRequest("/api/v1/auth/login", principalSchema, {
    method: "POST",
    body: JSON.stringify({ tenant_id: tenantId, username, password }),
  });
}

export function loadExperience() {
  return apiRequest("/api/v1/experience", experienceSchema);
}

export function createConversation(title: string) {
  return apiRequest("/api/v1/conversations", conversationSchema, {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export function sendMessage(conversationId: string, text: string, idempotencyKey: string) {
  return apiRequest(`/api/v1/conversations/${encodeURIComponent(conversationId)}/messages`, runSchema, {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: JSON.stringify({ text }),
  });
}

export function loadRun(runId: string) {
  return apiRequest(`/api/v1/runs/${encodeURIComponent(runId)}`, runSchema);
}

export function cancelRun(runId: string) {
  return apiRequest(`/api/v1/runs/${encodeURIComponent(runId)}/cancel`, runSchema, { method: "POST" });
}

export function listApprovals() {
  return apiRequest("/api/v1/approvals", z.array(approvalSchema));
}

export function decideApproval(approvalId: string, decision: "approved" | "rejected") {
  return apiRequest(`/api/v1/approvals/${encodeURIComponent(approvalId)}/decision`, z.null(), {
    method: "POST",
    body: JSON.stringify({ decision }),
  });
}

export function listArtifacts() {
  return apiRequest("/api/v1/artifacts", z.array(artifactSchema));
}

export function listMemory() {
  return apiRequest("/api/v1/memory", z.array(memorySchema));
}

export function deleteMemory(recordId: string) {
  return apiRequest(`/api/v1/memory/${encodeURIComponent(recordId)}`, z.null(), { method: "DELETE" });
}
