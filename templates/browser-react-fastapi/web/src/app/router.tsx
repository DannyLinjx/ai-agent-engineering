import { useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell, type ExperienceConfig, type Surface } from "./shell/AppShell";
import { ApprovalsPage } from "../features/approvals/ApprovalsPage";
import { ArtifactsPage } from "../features/artifacts/ArtifactsPage";
import { ConversationWorkspace } from "../features/conversations/ConversationWorkspace";
import { MemoryPage } from "../features/memory/MemoryPage";
import { RunInspector } from "../features/runs/RunInspector";

function Placeholder({ title, note }: { title: string; note: string }) {
  return <article className="placeholder"><span className="plate">MODULE</span><h2>{title}</h2><p>{note}</p></article>;
}

function ConversationRoute() {
  const [messages, setMessages] = useState<Array<{ id: string; role: "user" | "agent"; text: string; status?: string }>>([]);
  const [run, setRun] = useState<null | { id: string; status: string; plan: []; events: []; evidence: []; artifacts: []; costUsd: number }>(null);
  const send = (text: string) => {
    const id = crypto.randomUUID();
    setMessages((current) => [...current, { id, role: "user", text, status: "queued" }]);
    setRun({ id: crypto.randomUUID(), status: "queued", plan: [], events: [], evidence: [], artifacts: [], costUsd: 0 });
  };
  return <ConversationWorkspace conversations={[{ id: "current", title: "Current request", status: "active" }]} messages={messages} selectedConversationId="current" connection="live" run={run} onSend={send} onCancel={(runId) => setRun((current) => current && current.id === runId ? { ...current, status: "cancelling" } : current)} onRetry={() => undefined} onAttachmentRejected={(filename) => window.alert(`Attachment rejected by policy: ${filename}`)} />;
}

function surfaceElement(surface: Surface, title: string, note: string) {
  if (surface === "conversation") return <ConversationRoute />;
  if (surface === "run_inspector" || surface === "runs") return <RunInspector run={null} onRetry={() => undefined} />;
  if (surface === "approvals") return <ApprovalsPage state="empty" approvals={[]} onDecision={() => undefined} />;
  if (surface === "artifacts") return <ArtifactsPage artifacts={[]} onDownload={() => undefined} />;
  if (surface === "memory") return <MemoryPage state="empty" records={[]} onDelete={() => undefined} onCorrect={() => undefined} onExport={() => undefined} />;
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

export function AppRouter({ config }: { config: ExperienceConfig }) {
  const uniquePaths = new Set<string>();
  const routes = config.surfaces.flatMap((surface) => {
    const route = routeBySurface[surface];
    if (uniquePaths.has(route.path)) return [];
    uniquePaths.add(route.path);
    if ((surface === "settings" || surface === "access") && config.role !== "admin") return [];
    return [<Route key={surface} path={route.path} element={surfaceElement(surface, route.title, route.note)} />];
  });
  const fallback = config.surfaces.includes("conversation") ? "/conversation" : routeBySurface[config.surfaces[0]].path;
  return <AppShell config={config}><Routes>{routes}<Route path="*" element={<Navigate to={fallback} replace />} /></Routes></AppShell>;
}
