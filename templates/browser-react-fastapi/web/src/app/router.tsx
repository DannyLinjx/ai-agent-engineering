import { useCallback, useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate, Route, Routes } from "react-router-dom";

import { ApiError } from "./api/client";
import {
  cancelRun, createConversation, decideApproval, deleteMemory, listApprovals, listArtifacts, listMemory,
  loadRun, sendMessage, type RunProjection,
} from "./api/controlPlane";
import { useRunEvents } from "./events/useRunEvents";
import { AppShell, type ExperienceConfig, type Surface } from "./shell/AppShell";
import { ApprovalsPage } from "../features/approvals/ApprovalsPage";
import { AccessPage } from "../features/access/AccessPage";
import { ArtifactsPage } from "../features/artifacts/ArtifactsPage";
import { AuditPage } from "../features/audit/AuditPage";
import { CapabilitiesPage } from "../features/capabilities/CapabilitiesPage";
import { ConversationWorkspace } from "../features/conversations/ConversationWorkspace";
import { HealthPage } from "../features/health/HealthPage";
import { MemoryPage } from "../features/memory/MemoryPage";
import { ModelsPage } from "../features/models/ModelsPage";
import { OverviewPage } from "../features/overview/OverviewPage";
import { RunInspector } from "../features/runs/RunInspector";
import { SettingsPage } from "../features/settings/SettingsPage";

function Placeholder({ title, note }: { title: string; note: string }) {
  return <article className="placeholder"><span className="plate">MODULE</span><h2>{title}</h2><p>{note}</p></article>;
}

function PreviewConversationRoute() {
  const [messages, setMessages] = useState<Array<{ id: string; role: "user" | "agent"; text: string; status?: string }>>([]);
  const [run, setRun] = useState<null | { id: string; status: string; plan: []; events: []; evidence: []; artifacts: []; costUsd: number }>(null);
  const send = (text: string) => {
    const id = crypto.randomUUID();
    setMessages((current) => [...current, { id, role: "user", text, status: "queued" }]);
    setRun({ id: crypto.randomUUID(), status: "queued", plan: [], events: [], evidence: [], artifacts: [], costUsd: 0 });
  };
  return <ConversationWorkspace conversations={[{ id: "current", title: "Current request", status: "active" }]} messages={messages} selectedConversationId="current" connection="live" run={run} onSend={send} onCancel={(runId) => setRun((current) => current && current.id === runId ? { ...current, status: "cancelling" } : current)} onRetry={() => undefined} onAttachmentRejected={(filename) => window.alert(`Attachment rejected by policy: ${filename}`)} />;
}

function ConnectedConversationRoute() {
  const initialized = useRef(false);
  const [conversation, setConversation] = useState<{ id: string; title: string; status: string } | null>(null);
  const [messages, setMessages] = useState<Array<{ id: string; role: "user" | "agent"; text: string; status?: string }>>([]);
  const [projection, setProjection] = useState<RunProjection | null>(null);
  const [error, setError] = useState<string>();

  const createMutation = useMutation({
    mutationFn: () => createConversation("Current request"),
    onSuccess: (created) => setConversation(created),
    onError: (reason) => setError(reason instanceof Error ? reason.message : "Conversation creation failed"),
  });
  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    createMutation.mutate();
  }, [createMutation]);

  const refetchRun = useCallback(() => {
    if (!projection) return;
    void loadRun(projection.run_id).then(setProjection).catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : "Run refresh failed");
    });
  }, [projection]);
  const eventState = useRunEvents(projection?.run_id ?? null, refetchRun);

  const sendMutation = useMutation({
    mutationFn: ({ text, key }: { text: string; key: string }) => {
      if (!conversation) throw new Error("Conversation is not ready");
      return sendMessage(conversation.id, text, key);
    },
    onSuccess: (run, variables) => {
      setProjection(run);
      setMessages((current) => current.map((message) => message.id === variables.key ? { ...message, status: run.status } : message));
    },
    onError: (reason, variables) => {
      setMessages((current) => current.map((message) => message.id === variables.key ? { ...message, status: "failed" } : message));
      const suffix = reason instanceof ApiError && reason.correlationId ? ` · ${reason.correlationId}` : "";
      setError(`${reason instanceof Error ? reason.message : "Message failed"}${suffix}`);
    },
  });
  const cancelMutation = useMutation({
    mutationFn: cancelRun,
    onSuccess: setProjection,
    onError: (reason) => setError(reason instanceof Error ? reason.message : "Cancellation failed"),
  });

  const run = projection ? {
    id: projection.run_id,
    status: eventState.status === "idle" ? projection.status : eventState.status,
    plan: [],
    events: eventState.events.map((event) => ({
      id: event.id,
      type: event.type,
      status: event.status,
      summary: typeof event.payload.summary === "string" ? event.payload.summary : undefined,
    })),
    evidence: eventState.events.filter((event) => event.type === "evidence.added").map((event) => event.id),
    artifacts: eventState.events.filter((event) => event.type === "artifact.created").map((event) => ({ id: event.id, name: "Authorized artifact" })),
    costUsd: 0,
  } : null;
  const connection = projection
    ? (eventState.connection === "idle" ? "connecting" : eventState.connection)
    : "live";

  return <ConversationWorkspace
    conversations={conversation ? [conversation] : []}
    messages={messages}
    selectedConversationId={conversation?.id ?? null}
    connection={connection}
    run={run}
    error={error}
    onSend={(text) => {
      const key = crypto.randomUUID();
      setError(undefined);
      setMessages((current) => [...current, { id: key, role: "user", text, status: "sending" }]);
      sendMutation.mutate({ text, key });
    }}
    onCancel={(runId) => cancelMutation.mutate(runId)}
    onRetry={() => refetchRun()}
    onAttachmentRejected={(filename) => setError(`Attachment rejected by policy: ${filename}`)}
  />;
}

function ConnectedApprovalsRoute() {
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ["approvals"], queryFn: listApprovals });
  const decision = useMutation({
    mutationFn: ({ id, value }: { id: string; value: "approved" | "rejected" }) => decideApproval(id, value),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["approvals"] }),
  });
  const approvals = (query.data ?? []).map((item) => ({
    id: item.id, toolName: item.tool_name, toolVersion: item.tool_version, target: item.target, risk: item.risk,
    fingerprint: item.action_fingerprint, expiresAt: item.expires_at, evidenceRefs: item.evidence_refs, status: item.decision,
  }));
  const state = query.isPending ? "loading" : query.isError ? "error" : approvals.length ? "ready" : "empty";
  return <ApprovalsPage
    state={state}
    approvals={approvals}
    correlationId={query.error instanceof ApiError ? query.error.correlationId ?? undefined : undefined}
    onDecision={(id, value) => decision.mutate({ id, value })}
  />;
}

function ConnectedArtifactsRoute() {
  const query = useQuery({ queryKey: ["artifacts"], queryFn: listArtifacts });
  const artifacts = (query.data ?? []).map((item) => ({
    id: item.id, filename: item.filename, mediaType: item.media_type, sizeBytes: item.size_bytes,
    digest: item.digest, createdAt: item.created_at,
  }));
  return <ArtifactsPage
    state={query.isPending ? "loading" : query.isError ? "error" : "ready"}
    artifacts={artifacts}
    onDownload={(id) => window.location.assign(`/api/v1/artifacts/${encodeURIComponent(id)}/download`)}
  />;
}

function ConnectedMemoryRoute() {
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ["memory"], queryFn: listMemory });
  const remove = useMutation({
    mutationFn: deleteMemory,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["memory"] }),
  });
  const records = (query.data ?? []).map((item) => ({
    id: item.id, summary: item.summary, memoryType: item.memory_type, source: item.source,
    evidenceRefs: item.evidence_refs, confidence: item.confidence, sensitivity: item.sensitivity, status: item.status,
  }));
  const state = query.isPending ? "loading" : query.isError ? "error" : records.length ? "ready" : "empty";
  return <MemoryPage
    state={state}
    records={records}
    onDelete={(id) => remove.mutate(id)}
    onExport={() => window.location.assign("/api/v1/memory/export")}
  />;
}

function surfaceElement(surface: Surface, title: string, note: string, connected: boolean) {
  if (surface === "conversation") return connected ? <ConnectedConversationRoute /> : <PreviewConversationRoute />;
  if (surface === "run_inspector" || surface === "runs") return <RunInspector run={null} onRetry={() => undefined} />;
  if (surface === "approvals") return connected ? <ConnectedApprovalsRoute /> : <ApprovalsPage state="empty" approvals={[]} onDecision={() => undefined} />;
  if (surface === "artifacts") return connected ? <ConnectedArtifactsRoute /> : <ArtifactsPage artifacts={[]} onDownload={() => undefined} />;
  if (surface === "memory") return connected ? <ConnectedMemoryRoute /> : <MemoryPage state="empty" records={[]} onDelete={() => undefined} onCorrect={() => undefined} onExport={() => undefined} />;
  if (surface === "overview") return <OverviewPage state="empty" metrics={[]} />;
  if (surface === "audit") return <AuditPage events={[]} />;
  if (surface === "models") return <ModelsPage models={[]} />;
  if (surface === "capabilities") return <CapabilitiesPage capabilities={[]} />;
  if (surface === "settings") return <SettingsPage configFingerprint={null} pendingChanges={0} />;
  if (surface === "access") return <AccessPage principals={[]} />;
  if (surface === "health") return <HealthPage dependencies={[]} />;
  return <Placeholder title={title} note={note} />;
}

const routeBySurface: Record<Surface, { path: string; title: string; note: string }> = {
  conversation: { path: "/conversation", title: "Conversation", note: "Compose a bounded request and observe verified delivery." },
  run_inspector: { path: "/runs", title: "Run inspector", note: "Review safe Events, plan progress, receipts, and evidence." },
  runs: { path: "/runs", title: "Runs", note: "Inspect scoped current and historical Runs." },
  approvals: { path: "/approvals", title: "Approvals", note: "Decide exact parameter-bound actions before execution." },
  artifacts: { path: "/artifacts", title: "Artifacts", note: "Download authorized, content-addressed evidence." },
  memory: { path: "/memory", title: "Memory", note: "Review provenance, confidence, correction, expiry, and deletion." },
  overview: { path: "/overview", title: "Overview", note: "Operate from measured state, never hard-coded success." },
  audit: { path: "/audit", title: "Audit", note: "Trace decisions, actors, scopes, and correlation IDs." },
  models: { path: "/models", title: "Models", note: "View capability and fallback profiles without exposing credentials." },
  capabilities: { path: "/capabilities", title: "Capabilities", note: "Compare implemented, planned, blocked, and verified evidence." },
  settings: { path: "/settings", title: "Settings", note: "Change governed configuration through reviewed controls." },
  access: { path: "/access", title: "Access", note: "Administer scoped roles and sessions." },
  health: { path: "/health", title: "Health", note: "Observe dependency health, queues, recovery, and SLOs." },
};

export function AppRouter({ config, connected = false }: { config: ExperienceConfig; connected?: boolean }) {
  const uniquePaths = new Set<string>();
  const routes = config.surfaces.flatMap((surface) => {
    const route = routeBySurface[surface];
    if (uniquePaths.has(route.path)) return [];
    uniquePaths.add(route.path);
    if ((surface === "settings" || surface === "access") && config.role !== "admin") return [];
    return [<Route key={surface} path={route.path} element={surfaceElement(surface, route.title, route.note, connected)} />];
  });
  const fallback = config.surfaces.includes("conversation") ? "/conversation" : routeBySurface[config.surfaces[0]].path;
  return <AppShell config={config}><Routes>{routes}<Route path="*" element={<Navigate to={fallback} replace />} /></Routes></AppShell>;
}
