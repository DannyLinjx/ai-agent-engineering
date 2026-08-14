export type ApprovalView = {
  id: string;
  toolName: string;
  toolVersion: string;
  target: string;
  risk: string;
  fingerprint: string;
  expiresAt: string;
  evidenceRefs: string[];
  status: string;
};

type ViewState = "loading" | "empty" | "error" | "ready";

export function ApprovalsPage({ state, approvals, onDecision, correlationId }: { state: ViewState; approvals: ApprovalView[]; onDecision: (id: string, decision: "approved" | "rejected") => void; correlationId?: string }) {
  if (state === "loading") return <div className="module-state"><span className="loader" />Loading approvals…</div>;
  if (state === "error") return <div className="module-state error">Approvals could not be loaded. Correlation: {correlationId ?? "unavailable"}</div>;
  if (state === "empty" || !approvals.length) return <div className="module-state"><h2>No approvals need attention.</h2><p>Parameter-bound requests will appear here with expiry and evidence.</p></div>;
  return <div className="card-grid">{approvals.map((approval) => (
    <article key={approval.id} className="governance-card approval-card">
      <header><span className={`risk ${approval.risk}`}>{approval.risk} risk</span><small>Expires {approval.expiresAt}</small></header>
      <h2>{approval.toolName}<sup>v{approval.toolVersion}</sup></h2>
      <dl><div><dt>Target</dt><dd>{approval.target}</dd></div><div><dt>Fingerprint</dt><dd><code>{approval.fingerprint}</code></dd></div><div><dt>Evidence</dt><dd>{approval.evidenceRefs.join(", ") || "None supplied"}</dd></div></dl>
      <footer><button className="secondary-button" onClick={() => onDecision(approval.id, "rejected")}>Reject action</button><button className="primary-button" onClick={() => onDecision(approval.id, "approved")}>Approve exact action</button></footer>
    </article>
  ))}</div>;
}
